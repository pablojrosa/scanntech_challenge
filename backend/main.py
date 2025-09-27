from flask import Flask, request, jsonify
from flask_cors import CORS
from src.app.main_agent import main_agent
import traceback

app = Flask(__name__)
ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS(app,origins=ALLOWED_ORIGINS)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    historial = data.get('history_chat', [])

    try:
 
        chat_session = main_agent.start_chat(
            history=historial,
            enable_automatic_function_calling=True
        )
        response = chat_session.send_message(message)
        text_response = response.text

        print("text_response: ", text_response)

        return jsonify({
            'response': text_response
        })
    
    except Exception as e:
        print((f"❌ Error procesando mensaje: {str(e)}"))
        return jsonify({'error': f'Error procesando mensaje: {str(e)}'}), 500   
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
