import React, { useState, useEffect } from 'react';
import { getConversationMetrics } from '../api/chatService';
import './TableStyles.css';

function ConversationMetricsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await getConversationMetrics();
        setMetrics(data);
      } catch (err) {
        setError('No se pudieron cargar las métricas.');
      }
      setIsLoading(false);
    };
    fetchMetrics();
  }, []);

  if (isLoading) return <p>Cargando métricas...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="page-container">
      <h2>Métricas de Conversaciones en Vivo (Últimas 100)</h2>
      <div className="table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>Mensaje del Usuario</th> 
              <th>Mensaje del Bot</th>
              <th>Faithfulness</th>
              <th>Answer Relevancy</th>
              <th>Session ID</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((item) => (
              <tr key={item.message_id}>
                <td>{item.user_question}</td> 
                <td>{item.message_text}</td>
                <td>{item.faithfulness?.toFixed(2)}</td>
                <td>{item.answer_relevancy?.toFixed(2)}</td>
                <td>{item.session_id}</td>
                <td>{new Date(item.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ConversationMetricsPage;