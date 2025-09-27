const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/chat';

function formatHistoryForBackend(messages) {
  const conversationHistory = messages.slice(1);
  
  return conversationHistory.map(msg => ({
    role: msg.sender === 'user' ? 'user' : 'model',
    parts: [{ text: msg.text }]
  }));
}

export const sendMessageToBot = async (inputText, currentMessages) => {
  const historyForBackend = formatHistoryForBackend(currentMessages);

  const payload = {
    message: inputText,
    history_chat: historyForBackend
  };

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error desde el servidor:', errorData);
      return "Oops! Algo salió mal tratando de conectar con el bot.";
    }

    const data = await response.json();
    return data.response;

  } catch (error) {
    console.error("Error de conexión:", error);
    return "Oops! No pude conectarme al servidor. Asegúrate de que esté corriendo.";
  }
};