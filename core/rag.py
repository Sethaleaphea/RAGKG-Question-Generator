import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import FAISS_INDEX_PATH, CHUNKS_JSON_PATH, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# Initialize Neo4j connection
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Load FAISS index and stored text chunks
def load_knowledge_base():
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CHUNKS_JSON_PATH, "r") as f:
        chunks = json.load(f)
    return index, chunks

index, chunks = load_knowledge_base()
model = SentenceTransformer("all-MiniLM-L6-v2")

# Retrieve relevant content from FAISS
def search_topic_faiss(topic, top_k=5):
    topic_embedding = model.encode([topic])
    distances, indices = index.search(topic_embedding, top_k)
    retrieved_chunks = [chunks[idx] for idx in indices[0] if idx < len(chunks)]
    return retrieved_chunks

# Connect to Neo4j and retrieve knowledge
class KnowledgeGraphRetriever:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def retrieve_facts(self, topic):
        query = """
        MATCH (t:Topic {name: $topic})-[:BELONGS_TO]->(d:Document)
        RETURN d.text AS document_text
        """
        with self.driver.session() as session:
            result = session.run(query, topic=topic)
            return [record["document_text"] for record in result]

    def close(self):
        self.driver.close()

# Unified function to retrieve from both FAISS and Neo4j
def search_topic(topic, top_k=5):
    retriever = KnowledgeGraphRetriever()
    knowledge_facts = retriever.retrieve_facts(topic)
    retriever.close()

    text_chunks = search_topic_faiss(topic, top_k)
    return knowledge_facts + text_chunks  # Combine KG + FAISS knowledge

# Check if question already exists in Neo4j
def check_existing_question(tx, question_text):
    result = tx.run(
        "MATCH (q:Question {text: $question_text}) RETURN q",
        question_text=question_text
    )
    return result.single() is not None  # Returns True if the question exists

# Store generated question in Neo4j only if it doesn't already exist
def store_generated_question(topic, question_text, difficulty, question_type, correct_answer):
    with driver.session() as session:
        # Check if the question already exists
        if session.write_transaction(check_existing_question, question_text):
            print(f"Question already exists: {question_text}")
        else:
            # Insert question into Neo4j
            session.write_transaction(insert_question_into_neo4j, topic, question_text, difficulty, question_type, correct_answer)

def insert_question_into_neo4j(tx, topic, question, difficulty, question_type, correct_answer):
    tx.run(
        """
        MERGE (t:Topic {name: $topic})
        MERGE (q:Question {text: $question, difficulty: $difficulty, type: $question_type})
        MERGE (q)-[:BELONGS_TO]->(t)
        """,
        topic=topic, question=question, difficulty=difficulty, question_type=question_type
    )
    if correct_answer:
        tx.run(
            """
            MATCH (q:Question {text: $question})
            SET q.correct_answer = $correct_answer
            """,
            question=question, correct_answer=correct_answer
        )
