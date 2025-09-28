from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
from src.app.main_agent import main_agent
from src.app.rag_tool import semantic_search_raw
import os 
from flask_migrate import Migrate
from src.models import db, ChatMessage, ConversationEval, EvaluationResult, GoldenDataset
import threading
import numpy as np
from ragas import evaluate
from datasets import Dataset
from ragas.metrics import (
    faithfulness,
    answer_relevancy
)


app = Flask(__name__)
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)


db_url = os.environ.get('DATABASE_URL')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

def evaluate_interaction_async(app, question, answer, context, session_id, agent_message_id):
    with app.app_context():
        try:
            print(f"📊 Iniciando evaluación para el mensaje {agent_message_id}...")
            data = {
                "question": [question],
                "answer": [answer],
                "contexts": [[context]]
            }
            dataset = Dataset.from_dict(data)
            
            result = evaluate(
                dataset, 
                metrics=[faithfulness,
                         answer_relevancy
                         ]
            )
            
            new_evaluation = ConversationEval(
                message_id=agent_message_id,
                session_id=session_id,
                user_question=question,
                faithfulness=round(result['faithfulness'][0],2),
                answer_relevancy=round(result['answer_relevancy'][0],2)
            )
            
            db.session.add(new_evaluation)
            db.session.commit()
            print(f"✅ Evaluación para {agent_message_id} guardada exitosamente.")

        except Exception as e:
            print(f"❌ Error en la evaluación asíncrona para {agent_message_id}: {e}")
            db.session.rollback()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')
    historial = data.get('history_chat', [])

    if not message or not session_id:
        return jsonify({'error': 'Faltan los campos "message" o "session_id"'}), 400

    try:
        # save user message
        user_message = ChatMessage(session_id=session_id, sender='user', message=message)
        db.session.add(user_message)

        search_result = semantic_search_raw(message)
        context = search_result["context"]
        scores = search_result["scores"]
        avg_confidence = np.mean(scores) if scores else 0.0
    
        chat_session = main_agent.start_chat(history=historial, enable_automatic_function_calling=True)

        response = chat_session.send_message(message)
        text_response = response.text
        # save agent message
        agent_message = ChatMessage(session_id=session_id, sender='agent', message=text_response)
        db.session.add(agent_message)
        db.session.commit()

        agent_message_id = agent_message.message_id
        eval_thread = threading.Thread(
            target=evaluate_interaction_async,
            args=(
                current_app._get_current_object(),
                message,
                text_response,
                context,
                session_id,
                agent_message_id
            )
        )
        eval_thread.start()

        return jsonify({
            'response': text_response
        })
    
    except Exception as e:
        db.session.rollback()
        print((f"❌ Error procesando mensaje: {str(e)}"))
        return jsonify({'error': f'Error procesando mensaje: {str(e)}'}), 500   
    
@app.route('/offline-evaluation-results', methods=['GET'])
def get_offline_evaluation_results():
    """
    Endpoint para obtener los resultados de la última corrida de evaluación offline.
    """
    try:

        latest_run = db.session.query(EvaluationResult.run_id).order_by(EvaluationResult.run_timestamp.desc()).first()
        if not latest_run:
            return jsonify([])

        latest_run_id = latest_run[0]

        query = db.session.query(EvaluationResult, GoldenDataset).join(
            GoldenDataset, EvaluationResult.golden_dataset_id == GoldenDataset.id
        ).filter(EvaluationResult.run_id == latest_run_id).all()
        
        results_list = []
        for eval_result, golden_entry in query:
            results_list.append({
                'question': golden_entry.question,
                'generated_answer': eval_result.generated_answer,
                'faithfulness': eval_result.faithfulness,
                'answer_relevancy': eval_result.answer_relevancy,
                'context_precision': eval_result.context_precision,
                'context_recall': eval_result.context_recall,
                'answer_correctness': eval_result.answer_correctness
            })
            
        return jsonify(results_list)

    except Exception as e:
        print(f"❌ Error al obtener resultados de evaluación offline: {str(e)}")
        return jsonify({'error': f'Error obteniendo resultados: {str(e)}'}), 500

@app.route('/conversation-metrics', methods=['GET'])
def get_conversation_metrics():
    try:
        query = db.session.query(ConversationEval, ChatMessage).join(
            ChatMessage, ConversationEval.message_id == ChatMessage.message_id
        ).order_by(ConversationEval.timestamp.desc()).limit(100) # Traemos los últimos 100
        
        results = query.all()
        
        metrics_list = []
        for eval_result, chat_message in results:
            metrics_list.append({
                'message_id': eval_result.message_id,
                'user_question': eval_result.user_question,
                'message_text': chat_message.message,
                'faithfulness': eval_result.faithfulness,
                'answer_relevancy': eval_result.answer_relevancy,
                'session_id': eval_result.session_id,
                'timestamp': eval_result.timestamp.isoformat(),
            })
            
        return jsonify(metrics_list)

    except Exception as e:
        print(f"❌ Error al obtener métricas de conversación: {str(e)}")
        return jsonify({'error': f'Error obteniendo métricas: {str(e)}'}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
