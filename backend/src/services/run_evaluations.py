# run_evaluation.py

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)

# Importa los componentes de tu sistema RAG
from src.app.main_agent import main_agent
from src.app.rag_tool import semantic_search_raw

def run_offline_evaluation():
    """
    Este script ejecuta una evaluación completa del sistema RAG utilizando
    el golden_dataset almacenado en la base de datos de PostgreSQL.
    """
    # 1. Cargar variables de entorno y conectar a la BD
    load_dotenv()
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    if not db_url:
        raise ValueError("DATABASE_URL no encontrada. Asegúrate de que tu .env esté configurado.")

    print("🔌 Conectando a la base de datos...")
    engine = create_engine(db_url)
    
    # 2. Leer tu Golden Dataset desde Postgres a un DataFrame de Pandas
    query = "SELECT question, ground_truth FROM golden_dataset"
    df = pd.read_sql_query(query, engine)
    print(f"✅ Se cargaron {len(df)} preguntas desde la tabla golden_dataset.")

    # 3. Generar las respuestas ('answer') y los contextos ('contexts') de tu RAG
    results = []
    print("🚀 Ejecutando el sistema RAG para cada pregunta (esto puede tardar)...")
    for index, row in df.iterrows():
        question = row['question']
        
        # Llama a tus componentes RAG existentes
        search_result = semantic_search_raw(question)
        contexts = [search_result['context']] # Ragas espera una lista de strings
        
        chat_session = main_agent.start_chat()
        response = chat_session.send_message(question)
        answer = response.text
        
        results.append({
            "question": question,
            "ground_truth": row['ground_truth'],
            "answer": answer,
            "contexts": contexts
        })
    
    rag_results_df = pd.DataFrame(results)

    # 4. Preparar el Dataset para Ragas
    rag_results_df['ground_truths'] = rag_results_df['ground_truth'].apply(lambda x: [x]) 
    evaluation_dataset = Dataset.from_pandas(rag_results_df)

    # 5. Ejecutar la Evaluación Completa con Ragas (¡Ahora sí con todas las métricas!)
    print("📊 Iniciando la evaluación completa con Ragas...")
    result = evaluate(
        evaluation_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall, 
            answer_correctness
        ]
    )

    result_df = result.to_pandas()
    
    print(result_df[['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness']].mean())
    
    output_file = "evaluation_results.csv"
    result_df.to_csv(output_file, index=False)
    print(f"\nResultados detallados guardados en '{output_file}'")


if __name__ == '__main__':
    run_offline_evaluation()