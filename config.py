"""
Configuration settings for the hotel recommendation system.
"""
from pathlib import Path
from typing import Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Memory configuration
MEMORY_CONFIG = {
    "use_llm_memory": True,
    "save_conversations": True,
    "conversation_dir": str(DATA_DIR / "conversations"),
    "enable_vector_storage": True,
    "llm_analysis_timeout": 30,  # seconds
}

# Ollama LLM configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "qwen3:8b",  # or another model you have installed
    "timeout": 60,  # seconds
}

# Vector configuration
VECTOR_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",  # SentenceTransformers model
    "vector_dimension": 384,  # Depends on embedding model
    "vector_db_path": str(DATA_DIR / "vector_store"),
}

# Question configuration
QUESTIONS_CONFIG = {
    "min_answer_length": 10,  # characters
    "max_suggestions": 2,  # number of suggestions to offer if answer is insufficient
}

# CLI configuration
CLI_CONFIG = {
    "app_name": "gatherHotelPreferences",
    "app_version": "0.1.0",
}
