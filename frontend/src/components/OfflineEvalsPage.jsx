import React, { useState } from 'react';
import { runOfflineEvaluation } from '../api/chatService';
import './TableStyles.css';

function OfflineEvalsPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleRunEvaluation = async () => {
    setIsLoading(true);
    setError(null);
    setResults([]);
    try {
      const data = await runOfflineEvaluation();
      setResults(data);
    } catch (err) {
      setError('Hubo un error al ejecutar la evaluación. Revisa la consola del backend.');
    }
    setIsLoading(false);
  };

  return (
    <>
      <h2>Evaluación Offline del Sistema RAG</h2>
      <p>Haz clic para ejecutar el "Golden Dataset" contra el sistema RAG. Esto puede tardar varios minutos.</p>
      <p>Por una cuestion de tiempos y costos, solo se ejecutaran 2 registros del dataset</p>
      <button onClick={handleRunEvaluation} disabled={isLoading}>
        {isLoading ? 'Ejecutando...' : 'Iniciar Evaluación Offline'}
      </button>
      
      {error && <p className="error-message">{error}</p>}
      
      {results.length > 0 && (
        <div className="table-container">
          <h3>Resultados de la Evaluación</h3>
          <table className="results-table">
            <thead>
              <tr>
                <th>Pregunta</th>
                <th>Faithfulness</th>
                <th>Answer Relevancy</th>
                <th>Context Precision</th>
                <th>Context Recall</th>
                <th>Answer Correctness</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index}>
                  <td>{item.question}</td>
                  <td>{item.faithfulness?.toFixed(2)}</td>
                  <td>{item.answer_relevancy?.toFixed(2)}</td>
                  <td>{item.context_precision?.toFixed(2)}</td>
                  <td>{item.context_recall?.toFixed(2)}</td>
                  <td>{item.answer_correctness?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default OfflineEvalsPage;