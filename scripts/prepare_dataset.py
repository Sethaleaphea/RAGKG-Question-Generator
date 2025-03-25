import fitz  # PyMuPDF
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import PDF_FOLDER, OUTPUT_DIR, FAISS_INDEX_PATH, CHUNKS_JSON_PATH, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = " ".join([page.get_text() for page in doc])
        return text.replace("\n", " ")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

# Split text into chunks
def split_text(text, chunk_size=1000):
    sentences = text.split('. ')
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Process multiple PDFs
def process_pdfs():
    all_chunks = []
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, filename)
            text = extract_text_from_pdf(pdf_path)
            chunks = split_text(text)
            all_chunks.extend(chunks)
    return all_chunks

# Create and store FAISS index
def create_faiss_index(chunks):
    embeddings = np.vstack([model.encode(chunks[i:i+100]) for i in range(0, len(chunks), 100)])
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Save index and chunks in the structured directory
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_JSON_PATH, "w") as f:
        json.dump(chunks, f)

    print(f"Dataset processed and stored! Chunks saved: {len(chunks)}")

# Check if the chunk already exists in the Neo4j database
def is_chunk_existing(tx, chunk):
    result = tx.run(
        "MATCH (d:Document {text: $chunk}) RETURN d",
        chunk=chunk
    )
    return result.single() is not None

# Insert chunks into Neo4j and link to Topic
def insert_into_neo4j(tx, chunk, index, topic_name):
    if not is_chunk_existing(tx, chunk):
        tx.run(
            """
            MERGE (t:Topic {name: $topic_name})
            MERGE (d:Document {id: $index})  
            SET d.text = $chunk
            MERGE (d)-[:BELONGS_TO]->(t)
            """,
            topic_name=topic_name, index=index, chunk=chunk
        )
        print(f"Chunk {index} inserted.")
    else:
        print(f"Chunk {index} already exists, skipping.")

def store_chunks_in_neo4j(chunks, topic_name):
    with driver.session() as session:
        for i, chunk in enumerate(chunks):
            session.write_transaction(insert_into_neo4j, chunk, i, topic_name)

# Run processing
if __name__ == "__main__":
    topic_name = "SampleTopic"  # Use a sample topic or dynamically determine it based on the PDFs
    chunks = process_pdfs()
    create_faiss_index(chunks)
    store_chunks_in_neo4j(chunks, topic_name)  # Store chunks and link to Topic
