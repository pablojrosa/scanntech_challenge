from datasets import Dataset
from ragas.evaluation import evaluate
from ragas.metrics import faithfulness, answer_relevancy

from .models import db, ConversationEval

def run_online_evaluation(app, question, answer, context, session_id, agent_message_id):
    """
    Esta función ahora vive en su propio módulo.
    Ejecuta la evaluación de Ragas para una sola interacción.
    """
    with app.app_context():
        try:
            print(f"📊 Iniciando evaluación online para el mensaje {agent_message_id}...")
            data = {
                "question": [question],
                "answer": [answer],
                "contexts": [[context]]
            }
            dataset = Dataset.from_dict(data)
            
            result = evaluate(
                dataset, 
                metrics=[faithfulness, answer_relevancy]
            )
            
            new_evaluation = ConversationEval(
                message_id=agent_message_id,
                user_question=question,
                session_id=session_id,
                faithfulness=round(result['faithfulness'][0], 2),
                answer_relevancy=round(result['answer_relevancy'][0], 2)
            )
            
            db.session.add(new_evaluation)
            db.session.commit()
            print(f"✅ Evaluación online para {agent_message_id} guardada exitosamente.")

        except Exception as e:
            print(f"❌ Error en la evaluación online para {agent_message_id}: {e}")
            db.session.rollback()