"""
This module provides an implementation of the EmbeddingGenerator protocol
using a local sentence-transformer model.
"""
import logging
from typing import List, Dict, Any

from axiom.core.interfaces import DocumentChunk, EmbeddingGenerator

class LocalEmbeddingGenerator(EmbeddingGenerator):
    """
    Generates vector embeddings for document chunks using a local
    sentence-transformer model.
    """

    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "The 'sentence-transformers' library is required for LocalEmbeddingGenerator. "
                "Please install it with 'pip install sentence-transformers'."
            )
        
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        try:
            self.logger.info(f"Loading local sentence-transformer model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info("Successfully loaded model.")
        except Exception as e:
            self.logger.error(f"Failed to load sentence-transformer model '{self.model_name}': {e}", exc_info=True)
            raise RuntimeError(f"Could not load local model '{self.model_name}'.") from e

    def embed_batch(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """
        Generates embeddings for a batch of document chunks.

        Args:
            chunks: A list of DocumentChunk objects to be embedded.

        Returns:
            A list of vector embeddings, where each embedding corresponds to a chunk.
        """
        if not chunks:
            return []

        texts_to_embed = [chunk.text for chunk in chunks]
        
        self.logger.info(f"Generating embeddings for {len(texts_to_embed)} chunks using local model '{self.model_name}'...")
        
        try:
            embeddings = self.model.encode(texts_to_embed, convert_to_numpy=False)
            self.logger.info("Successfully generated embeddings.")
            # The model.encode can return a list of arrays, so ensure it's lists of floats
            return [list(map(float, emb)) for emb in embeddings]
        except Exception as e:
            self.logger.error(f"An error occurred during local embedding generation: {e}", exc_info=True)
            raise RuntimeError("Failed to generate embeddings with the local model.") from e

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Returns information about the embedding provider.
        """
        return {
            "provider_name": "local",
            "model_name": self.model_name
        }

