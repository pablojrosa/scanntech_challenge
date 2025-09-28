import React, { useState, useEffect } from 'react';
import { getOfflineEvaluationResults } from '../api/chatService';
import './TableStyles.css';

function OfflineEvalsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getOfflineEvaluationResults();
        setResults(data);
      } catch (err) {
        setError('No se pudieron cargar los resultados. Ejecuta una evaluación desde tu terminal.');
      }
      setIsLoading(false);
    };
    fetchResults();
  }, []);

  if (isLoading) return <p>Cargando resultados de la última evaluación...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="page-container">
      <h2>Resultados de la Última Evaluación Offline</h2>
      <p>
        Estos son los scores de la última evaluación ejecutada con <code>python run_evaluations.py</code>.
      </p>
      
      {results.length > 0 ? (
        <div className="table-container">
          <h3>Resultados de la Evaluación</h3>
          <table className="results-table">
            <thead>
              <tr>
                <th>Pregunta</th>
                <th>Respuesta Generada</th> 
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
                  <td>{item.generated_answer}</td> 
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
      ):(<p>No se encontraron resultados. ¿Ya ejecutaste una evaluación?</p>
      )}
    </div>
  );
}

export default OfflineEvalsPage;