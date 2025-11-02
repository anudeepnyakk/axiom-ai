"""
This module provides an implementation of the EmbeddingGenerator protocol
using OpenAI's powerful embedding models.
"""
import logging
from typing import List, Dict, Any
from openai import OpenAI
from axiom.core.interfaces import DocumentChunk, EmbeddingGenerator

# Recommended by OpenAI for most use cases
# See: https://platform.openai.com/docs/guides/embeddings/embedding-models
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

class OpenAIEmbeddingGenerator(EmbeddingGenerator):
    """
    Generates vector embeddings for document chunks using the OpenAI API.
    """

    def __init__(self, api_key: str, model_name: str = DEFAULT_EMBEDDING_MODEL):
        if not api_key:
            raise ValueError("OpenAI API key is required but was not provided.")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized OpenAIEmbeddingGenerator with model: {self.model_name}")

    def embed_batch(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """
        Generates embeddings for a batch of document chunks.

        Args:
            chunks: A list of DocumentChunk objects to be embedded.

        Returns:
            A list of vector embeddings, where each embedding corresponds to a chunk.
        
        Raises:
            RuntimeError: If the API call to OpenAI fails.
        """
        if not chunks:
            return []

        texts_to_embed = [chunk.text for chunk in chunks]
        
        self.logger.info(f"Generating embeddings for {len(texts_to_embed)} chunks using '{self.model_name}'...")
        
        try:
            response = self.client.embeddings.create(
                input=texts_to_embed,
                model=self.model_name
            )
            embeddings = [item.embedding for item in response.data]
            self.logger.info("Successfully generated embeddings.")
            return embeddings
        except Exception as e:
            self.logger.error(f"An error occurred with the OpenAI embedding API call: {e}", exc_info=True)
            raise RuntimeError("Failed to generate embeddings due to an API error.") from e

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Returns information about the embedding provider.
        """
        return {
            "provider_name": "openai",
            "model_name": self.model_name
        }
