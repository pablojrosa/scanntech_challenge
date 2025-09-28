import os
from pinecone import Pinecone
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
top_k = 3
PINECONE_API_KEY =os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
pc = Pinecone(api_key=PINECONE_API_KEY)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"El índice '{PINECONE_INDEX_NAME}' no existe en Pinecone.")

index = pc.Index(PINECONE_INDEX_NAME)

def get_embedding(text: str):
    """Genera embedding de una consulta."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def semantic_search(query: str, top_k: int = top_k) -> str:
    """
    Busca y recupera pasajes de texto directamente del libro "An Introduction to Statistical Learning with Applications in Python".
    Utiliza esta herramienta SIEMPRE que el usuario pregunte por conceptos, definiciones, algoritmos o ejemplos del libro.
    Parámetros:
      - query (str): La pregunta del usuario o los conceptos clave a buscar. Por ejemplo: "explicación de k-means" o "diferencia entre Lasso y Ridge".
    """
    query_vector = get_embedding(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    text_response = ""
    for match in results["matches"]:
        text = match["metadata"]["text"].replace("\n", " ")
        text_response += f"{text}\n\n"
    return text_response.strip()


def semantic_search_raw(query: str, top_k: int = 3) -> dict:
    """
    Busca, recupera pasajes de texto y sus scores de confianza.
    Utiliza esta herramienta SIEMPRE que el usuario pregunte por conceptos, definiciones, etc.
    Devuelve un diccionario con el contexto y los scores.
    """
    query_vector = get_embedding(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    contexts = []
    scores = []

    if "matches" in results:
        for match in results["matches"]:
            text = match["metadata"]["text"].replace("\n", " ")
            contexts.append(text)

            if "score" in match:
                scores.append(match["score"])

    final_context = "\n\n".join(contexts)

    return {
        "context": final_context,
        "scores": scores
    }