"""
Configuration management module.

Loads and validates environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """
    Application configuration with validation.

    All settings are loaded from environment variables with sensible defaults.
    """

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    # Vector Database Configuration
    vector_db_path: str = Field(default="./chroma_db", description="Path to ChromaDB storage")
    collection_name: str = Field(default="ecommerce_policies", description="ChromaDB collection name")

    # RAG Configuration
    chunk_size: int = Field(default=1000, description="Text chunk size for document splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between text chunks")
    top_k_results: int = Field(default=3, description="Number of documents to retrieve")

    # Model Configuration
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    llm_model: str = Field(default="gpt-4o-mini", description="OpenAI LLM model")

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        """Ensure API key is not empty or placeholder."""
        if not v or v == "your_openai_api_key_here":
            raise ValueError(
                "OpenAI API key not set. Please set OPENAI_API_KEY in .env file"
            )
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    class Config:
        """Pydantic config."""
        env_file = '.env'
        case_sensitive = False


def load_config() -> Config:
    """
    Load and validate application configuration.

    Returns:
        Config: Validated configuration object

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    try:
        config = Config(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./chroma_db"),
            collection_name=os.getenv("COLLECTION_NAME", "ecommerce_policies"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            top_k_results=int(os.getenv("TOP_K_RESULTS", "3")),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        )
        return config
    except ValueError as e:
        raise ValueError(f"Configuration error: {str(e)}")


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    directories = [
        Path("logs"),
        Path("data/sample_policies"),
        Path(os.getenv("VECTOR_DB_PATH", "./chroma_db")).parent,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
