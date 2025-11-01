from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ApiKeysConfig:
    """Stores API keys, loaded from config."""
    openai: str = ""

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    device: str = "cpu"

@dataclass
class DocumentProcessingConfig:
    """Configuration for processing documents."""
    chunk_size: int = 800
    chunk_overlap: int = 160
    max_file_size_mb: int = 50

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    log_file: str = "axiom.log"
    log_to_console: bool = True
    log_to_file: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class StateTrackerConfig:
    """Configuration for the state tracker database."""
    db_path: str = "axiom_state.db"
    auto_cleanup_days: int = 30

@dataclass
class VectorStoreConfig:
    """Configuration for the vector store (e.g., ChromaDB)."""
    persist_directory: str = "./chroma_db/axiom_documents"
    collection_name: str = "axiom_documents"

@dataclass
class Config:
    """Root configuration object for the entire application."""
    document_processing: DocumentProcessingConfig
    embeddings: EmbeddingConfig
    logging: LoggingConfig
    state_tracker: StateTrackerConfig
    vector_store: VectorStoreConfig
    api_keys: ApiKeysConfig
    data_dir: str = "axiom/data"

    @classmethod
    def create_default(cls):
        """Creates a default configuration object."""
        return cls(
            document_processing=DocumentProcessingConfig(),
            embeddings=EmbeddingConfig(),
            logging=LoggingConfig(),
            state_tracker=StateTrackerConfig(),
            vector_store=VectorStoreConfig(),
            api_keys=ApiKeysConfig()
        )




