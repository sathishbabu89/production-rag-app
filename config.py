import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    MODEL_NAME = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
    
    # Embeddings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector DB
    CHROMA_PATH = "chroma_db"

    # Retrieval
    TOP_K = 3

    MMR_FETCH_K = 10
    MMR_LAMBDA = 0.5

    # Reranker
    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # -----------------------------
    # Reranker Threshold Filtering
    # -----------------------------

    RERANKER_SCORE_THRESHOLD = -2.0
    MIN_RERANKED_RESULTS = 1

    # -----------------------------
    # Score Gap Filtering
    # -----------------------------

    ENABLE_SCORE_GAP_FILTERING = True
    RERANKER_SCORE_GAP_THRESHOLD = 5.0