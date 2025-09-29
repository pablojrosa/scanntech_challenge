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
      <div className="metrics-description">
        <h4>¿Qué significa cada métrica?</h4>
        <dl>
          <dt><strong>Faithfulness (Fidelidad):</strong></dt>
          <dd>
            Mide si la respuesta generada se basa ÚNICAMENTE en el contexto proporcionado. Un score alto (cercano a 1) significa que el modelo no está "alucinando" o inventando información.
          </dd>
          <dt><strong>Answer Relevancy (Relevancia de la Respuesta):</strong></dt>
          <dd>
            Evalúa si la respuesta es pertinente y responde directamente a la pregunta del usuario. Un score bajo podría indicar que la respuesta es vaga o se va por las ramas.
          </dd>
        </dl>
      </div>
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