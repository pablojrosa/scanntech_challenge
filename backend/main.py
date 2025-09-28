from flask import Flask, request, jsonify
from flask_cors import CORS
from src.app.main_agent import main_agent
import os 
from flask_migrate import Migrate
from src.models import db, ChatMessage


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
        
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')
    historial = data.get('history_chat', [])

    try:
        # save user message
        user_message = ChatMessage(session_id=session_id, sender='user', message=message)
        db.session.add(user_message)
    
        chat_session = main_agent.start_chat(history=historial, enable_automatic_function_calling=True)

        response = chat_session.send_message(message)
        text_response = response.text
        # save agent message
        agent_message = ChatMessage(session_id=session_id, sender='agent', message=text_response)
        db.session.add(agent_message)
        
        db.session.commit()

        return jsonify({
            'response': text_response
        })
    
    except Exception as e:
        print((f"❌ Error procesando mensaje: {str(e)}"))
        return jsonify({'error': f'Error procesando mensaje: {str(e)}'}), 500   
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
