import os
from pathlib import Path
from dotenv import load_dotenv
# .env dosyasını yükler
load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

LLM_MODEL="nvidia/nemotron-3-ultra-550b-a55b:free"
DB_FAISS_PATH="vectorstore/db_faiss"
DATA_PATH="data/"
CHUNK_SIZE=500
CHUNK_OVERLAP=50