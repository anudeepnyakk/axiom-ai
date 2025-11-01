#!/usr/bin/env python3
"""
EmbeddingGenerator implementation using sentence-transformers.
Converts DocumentChunk objects into vector embeddings.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from ..core.interfaces import EmbeddingGenerator, DocumentChunk


class SentenceTransformerEmbeddingGenerator(EmbeddingGenerator):
    """
    Implementation of EmbeddingGenerator using sentence-transformers.
    
    Architecture: Wraps sentence-transformers with our protocol interface
    Strategy: Uses 'all-MiniLM-L6-v2' for balanced speed/quality
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Sentence transformer model to use
            device: Device to run on ('cpu', 'cuda', etc.)
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.device = device
        
        # Lazy loading - only load model when first used
        self._model: Optional[SentenceTransformer] = None
        self._embedding_dimension: Optional[int] = None
        
        self.logger.info(f"Initialized EmbeddingGenerator with model: {model_name}")
    
    def _ensure_model_loaded(self) -> None:
        """Lazy load the model when first needed."""
        if self._model is None:
            try:
                self.logger.info(f"Loading sentence transformer model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name, device=self.device)
                self._embedding_dimension = self._model.get_sentence_embedding_dimension()
                self.logger.info(f"Model loaded successfully. Embedding dimension: {self._embedding_dimension}")
            except Exception as e:
                self.logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
    
    def embed_batch(self, chunks: List[DocumentChunk]) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of document chunks.
        
        Architecture: Batch processing for efficiency
        Strategy: Convert chunks to text, batch embed, return numpy arrays
        """
        if not chunks:
            return []
        
        self._ensure_model_loaded()
        
        # Extract text from chunks
        texts = [chunk.text for chunk in chunks]
        
        try:
            # Generate embeddings in batch
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            
            # Handle single vs multiple embeddings
            if len(chunks) == 1:
                embeddings = [embeddings]
            
            self.logger.info(f"Generated {len(embeddings)} embeddings for {len(chunks)} chunks")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings for batch: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Architecture: Single text processing
        Strategy: Delegate to batch processing for consistency
        """
        if not text.strip():
            raise ValueError("Cannot embed empty text")
        
        # Create a dummy chunk for consistency
        dummy_chunk = DocumentChunk(text=text, metadata={})
        embeddings = self.embed_batch([dummy_chunk])
        return embeddings[0]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Architecture: Model introspection
        Strategy: Return model metadata for debugging/monitoring
        """
        self._ensure_model_loaded()
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self._embedding_dimension,
            "device": self.device,
            "model_type": "sentence_transformer"
        }
    
    def validate_model(self) -> bool:
        """
        Validate that the model is working correctly.
        
        Architecture: Health check
        Strategy: Test embedding generation on simple text
        """
        try:
            # Test with simple text
            test_text = "Hello, world!"
            embedding = self.embed_text(test_text)
            
            # Verify embedding properties
            if embedding is None or len(embedding) == 0:
                return False
            
            expected_dim = self.get_model_info()["embedding_dimension"]
            if len(embedding) != expected_dim:
                return False
            
            self.logger.info("Model validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Model validation failed: {e}")
            return False
