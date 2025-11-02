"""
Mock Embedding Generator for local/demo use
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from axiom.core.interfaces import DocumentChunk


class MockEmbeddingGenerator:
    def __init__(self, model_name: str = "mock-model", device: Optional[str] = "cpu"):
        self.model_name = model_name
        self.device = device
        self.embedding_dimension = 384
        self._logger = logging.getLogger(__name__)
        self._logger.info(f"Initialized MockEmbeddingGenerator: {model_name}")

    def embed_batch(self, chunks: List[DocumentChunk]) -> List[np.ndarray]:
        if not chunks:
            return []
        embeddings: List[np.ndarray] = []
        for chunk in chunks:
            seed = hash(chunk.text) % 1000000
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(self.embedding_dimension).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        self._logger.info(f"Generated {len(embeddings)} mock embeddings")
        return embeddings

    def embed_text(self, text: str) -> np.ndarray:
        dummy_chunk = DocumentChunk(text=text, metadata={})
        return self.embed_batch([dummy_chunk])[0]

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "device": self.device,
            "model_type": "mock",
        }

    def validate_model(self) -> bool:
        return True
