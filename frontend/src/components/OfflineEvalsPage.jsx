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

          <dt><strong>Context Precision (Precisión del Contexto):</strong></dt>
          <dd>
            Se enfoca en el paso de "Retrieval". Mide qué tan relevante es el contexto que se recuperó para responder la pregunta. Un score alto indica que no se trajo "ruido" o información inútil.
          </dd>

          <dt><strong>Context Recall (Exhaustividad del Contexto):</strong></dt>
          <dd>
            También evalúa el "Retrieval". Mide si se recuperó TODA la información necesaria del texto original para responder completamente la pregunta. Un score bajo sugiere que se omitieron partes importantes.
          </dd>

          <dt><strong>Answer Correctness (Corrección de la Respuesta):</strong></dt>
          <dd>
            Compara la respuesta generada con una respuesta "perfecta" (Ground Truth). Mide la exactitud y completitud de la respuesta. Es la métrica de calidad más completa, pero requiere un dataset de evaluación.
          </dd>
        </dl>
      </div>
      
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