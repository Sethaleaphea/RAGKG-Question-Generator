import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_FOLDER = os.path.join(BASE_DIR, "data", "books")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
FAISS_INDEX_PATH = os.path.join(OUTPUT_DIR, "faiss_index.bin")
CHUNKS_JSON_PATH = os.path.join(OUTPUT_DIR, "chunks.json")


# API Key (Use environment variable in production)
API_KEY = "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"

NEO4J_URI = "neo4j+s://09afc869.databases.neo4j.io"  # Update with your actual Neo4j URI
NEO4J_USER = "neo4j"  # Your Neo4j username
NEO4J_PASSWORD = "bojBh_4sxiQ590V1vqSTNfBQ6jfCN-zQkdsph9LMeWo"  # Your Neo4j password