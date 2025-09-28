const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

function formatHistoryForBackend(messages) {
  const conversationHistory = messages.slice(1);
  
  return conversationHistory.map(msg => ({
    role: msg.sender === 'user' ? 'user' : 'model',
    parts: [{ text: msg.text }]
  }));
}

export const sendMessageToBot = async (inputText, currentMessages, sessionId) => {
  const historyForBackend = formatHistoryForBackend(currentMessages);

  const payload = {
    message: inputText,
    history_chat: historyForBackend,
    session_id: sessionId
  };

  try {
    const response = await fetch(`${API_URL}/chat`, {
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

export const runOfflineEvaluation = async () => {
  try {
    const response = await fetch(`${API_URL}/evaluate-offline`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Error del servidor al ejecutar la evaluación.');
    return await response.json();
  } catch (error) {
    console.error("Error al ejecutar la evaluación offline:", error);
    throw error;
  }
};

export const getConversationMetrics = async () => {
  try {
    const response = await fetch(`${API_URL}/conversation-metrics`);
    if (!response.ok) throw new Error('Error del servidor al obtener las métricas.');
    return await response.json();
  } catch (error) {
    console.error("Error al obtener las métricas de conversación:", error);
    throw error;
  }
};
