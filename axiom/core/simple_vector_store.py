"""
Simple In-Memory Vector Store - For Testing

This provides a reliable vector store implementation for testing
the complete RAG pipeline without external dependencies.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from axiom.core.interfaces import VectorStore, DocumentChunk
from sklearn.metrics.pairwise import cosine_similarity


class SimpleVectorStore(VectorStore):
    """
    Simple in-memory vector store using numpy and cosine similarity
    
    This is perfect for testing and demonstration purposes.
    """
    
    def __init__(self, collection_name: str = "axiom_documents"):
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # In-memory storage
        self.vectors: List[np.ndarray] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []
        
        self.logger.info(f"Initialized SimpleVectorStore: {collection_name}")
    
    def init_collection(self, embedding_dimension: int) -> None:
        """Initialize collection (no-op for in-memory store)"""
        self.logger.info(f"Collection '{self.collection_name}' initialized for dimension {embedding_dimension}")
    
    def add(self, chunks: List[DocumentChunk], embeddings: List[np.ndarray], 
            ids: Optional[List[str]] = None) -> List[str]:
        """Add chunks with embeddings to the store"""
        if not chunks or not embeddings:
            return []
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks count ({len(chunks)}) must match embeddings count ({len(embeddings)})")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"chunk_{i}_{hash(chunk.text) % 1000000}" for i, chunk in enumerate(chunks)]
        
        # Store vectors and metadata
        for chunk, embedding, chunk_id in zip(chunks, embeddings, ids):
            self.vectors.append(embedding)
            self.metadatas.append({
                'text': chunk.text,
                'source': chunk.metadata.get('source', 'Unknown'),
                'chunk_id': chunk_id,
                **chunk.metadata  # Include all original metadata
            })
            self.ids.append(chunk_id)
        
        self.logger.info(f"Added {len(chunks)} chunks to vector store")
        return ids
    
    def upsert(self, chunks: List[DocumentChunk], embeddings: List[np.ndarray], 
               ids: List[str]) -> List[str]:
        """Update existing chunks or insert new ones"""
        # For simplicity, just delete and re-add
        for chunk_id in ids:
            if chunk_id in self.ids:
                idx = self.ids.index(chunk_id)
                del self.vectors[idx]
                del self.metadatas[idx]
                del self.ids[idx]
        
        return self.add(chunks, embeddings, ids)
    
    def delete(self, ids: List[str]) -> None:
        """Delete chunks by their IDs"""
        for chunk_id in ids:
            if chunk_id in self.ids:
                idx = self.ids.index(chunk_id)
                del self.vectors[idx]
                del self.metadatas[idx]
                del self.ids[idx]
        
        self.logger.info(f"Deleted {len(ids)} chunks from vector store")
    
    def get(self, ids: List[str]) -> List[Tuple[DocumentChunk, np.ndarray]]:
        """Get chunks and embeddings by IDs"""
        results = []
        for chunk_id in ids:
            if chunk_id in self.ids:
                idx = self.ids.index(chunk_id)
                metadata = self.metadatas[idx]
                chunk = DocumentChunk(
                    text=metadata['text'],
                    metadata=metadata
                )
                results.append((chunk, self.vectors[idx]))
        
        return results
    
    def count(self) -> int:
        """Get total number of vectors"""
        return len(self.vectors)
    
    def search_by_text(self, query_text: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search by text (requires embedding the query first)"""
        # This would need an embedding generator
        # For now, return empty results
        return []
    
    def search_by_vector(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search by vector using cosine similarity"""
        if not self.vectors:
            return []
        
        # Calculate cosine similarities
        similarities = []
        for vector in self.vectors:
            # Ensure vectors are 2D for sklearn
            if vector.ndim == 1:
                vector_2d = vector.reshape(1, -1)
                query_2d = query_vector.reshape(1, -1)
            else:
                vector_2d = vector
                query_2d = query_vector
            
            similarity = cosine_similarity(query_2d, vector_2d)[0][0]
            similarities.append(similarity)
        
        # Sort by similarity and get top_k
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in sorted_indices:
            metadata = self.metadatas[idx]
            chunk = DocumentChunk(
                text=metadata['text'],
                metadata=metadata
            )
            results.append((chunk, similarities[idx]))
        
        return results
    
    def stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return {
            "total_vectors": len(self.vectors),
            "collection_name": self.collection_name,
            "store_type": "simple_in_memory"
        }
    
    def clear(self) -> None:
        """Clear all data"""
        self.vectors.clear()
        self.metadatas.clear()
        self.ids.clear()
        self.logger.info("Vector store cleared")
    
    def persist(self) -> None:
        """Persist data (no-op for in-memory store)"""
        self.logger.info("Data is already in memory (no persistence needed)")
