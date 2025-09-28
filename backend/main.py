from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
from src.app.main_agent import main_agent
from src.app.rag_tool import semantic_search_raw
import os 
from flask_migrate import Migrate
from src.models import db, ChatMessage, ConversationEval
import threading
import numpy as np
from ragas import evaluate
from datasets import Dataset
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)


app = Flask(__name__)
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
CORS(app,origins=allowed_origins)

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
                         answer_relevancy,
                         #context_precision,
                         #context_recall
                         ]
            )
            
            new_evaluation = ConversationEval(
                message_id=agent_message_id,
                session_id=session_id,
                faithfulness=round(result['faithfulness'][0],2),
                answer_relevancy=round(result['answer_relevancy'][0],2),
                context_precision=None,
                context_recall=None
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
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
