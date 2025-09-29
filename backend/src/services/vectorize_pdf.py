import os
from dotenv import load_dotenv
from pypdf import PdfReader
from pinecone import Pinecone
import openai
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
from pathlib import Path


load_dotenv()

try:
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY =os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    openai.api_key = OPENAI_API_KEY
    
except Exception as e:
    raise RuntimeError(f"Error al inicializar los clientes. Revisá tus API keys. Error: {e}")

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extrae texto página por página con metadatos."""
    print(f"Extrayendo texto de {pdf_path}...")
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            pages.append({"page": i, "text": text})
    print(f"Extracción completada: {len(pages)} páginas extraídas.")
    return pages

def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [d.embedding for d in response.data]


def chunk_text(text: str) -> list[str]:
    """
    Divide texto en chunks con superposición mínima, respetando párrafos/secciones.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", "? ", "! ", ", ", " ", ""]
    )
    return text_splitter.split_text(text)


def index_pdf_to_pinecone(pdf_path: str):
    """
    Proceso completo: extrae, chardea, vectoriza y sube un PDF a Pinecone.
    """
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        raise ValueError(f"El índice '{PINECONE_INDEX_NAME}' no existe.")
    index = pc.Index(PINECONE_INDEX_NAME)

    pages = extract_text_from_pdf(pdf_path)

    all_chunks = []
    for page in pages:
        chunks = chunk_text(page["text"])
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    batch_size = 50
    print(f"Vectorizando y subiendo {len(all_chunks)} chunks a Pinecone (batch={batch_size})...")

    for i in tqdm(range(0, len(all_chunks), batch_size)):
        batch_chunks = all_chunks[i: i + batch_size]
        batch_texts = [c["text"] for c in batch_chunks]

        embeddings = get_embeddings(batch_texts)
        vectors_to_upsert = []

        for j, (chunk_data, embedding) in enumerate(zip(batch_chunks, embeddings)):
            vector_id = f"{os.path.basename(pdf_path)}-chunk-{i+j}"
            metadata = {
                "text": chunk_data["text"],
                "page": chunk_data["page"],
                "source": os.path.basename(pdf_path)
            }
            vectors_to_upsert.append((vector_id, embedding, metadata))

        index.upsert(vectors=vectors_to_upsert)
        time.sleep(0.2)

    print("\n✅ ¡Proceso completado! El libro fue vectorizado con vectores densos y subido a Pinecone.")
    stats = index.describe_index_stats()
    print(f"📊 Estadísticas del índice: {stats}")


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    backend_root = script_path.parent.parent.parent
    pdf_file_path = backend_root / "data" / "PDF-GenAI-Challenge.pdf"

    if not os.path.exists(pdf_file_path):
        print(f"❌ Error: El archivo {pdf_file_path} no fue encontrado.")
    else:
        print("✅ Archivo PDF encontrado. Iniciando la vectorización...")
        index_pdf_to_pinecone(pdf_file_path)