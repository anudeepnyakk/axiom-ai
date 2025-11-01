#!/usr/bin/env python3
"""
VectorStore implementation using ChromaDB.
Stores and retrieves vector embeddings with metadata.
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None

from axiom.core.interfaces import VectorStore, DocumentChunk, EmbeddingGenerator


class ChromaVectorStore(VectorStore):
    """
    A persistent vector store using ChromaDB.
    """

    def __init__(self, embedding_generator: EmbeddingGenerator, persist_directory: str, collection_name: str = "axiom_documents"):
        self.embedding_generator = embedding_generator
        self.persist_directory = persist_directory
        self.default_collection_name = collection_name
        self._logger = logging.getLogger(__name__)
        self._client = chromadb.PersistentClient(path=self.persist_directory)
        self._collection = None
        self._logger.info(f"Initialized ChromaVectorStore: {self.persist_directory}")

    def get_or_create_collection(self, name: str) -> chromadb.Collection:
        if self._collection and self._collection.name == name:
            return self._collection
        try:
            self._collection = self._client.get_collection(name)
            self._logger.info(f"Retrieved existing collection: {name}")
        except:
            self._collection = self._client.create_collection(
                name=name,
                metadata={"description": "Axiom document embeddings"}
            )
            self._logger.info(f"Created new collection: {name}")
        return self._collection

    def init_collection(self, embedding_dimension: int) -> None:
        """
        Initialize the collection with specified embedding dimension.
        
        Architecture: Collection setup
        Strategy: Validate dimension and ensure collection exists
        """
        self._ensure_collection_initialized()
        
        # ChromaDB automatically handles embedding dimensions
        # We just need to ensure the collection is ready
        self._logger.info(f"Collection '{self.default_collection_name}' initialized for dimension {embedding_dimension}")
    
    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]], collection_name: Optional[str] = None) -> List[str]:
        """
        Adds document chunks and their embeddings to the vector store.
        """
        if not chunks:
            return []

        if len(chunks) != len(embeddings):
            raise ValueError(f"The number of chunks ({len(chunks)}) must match the number of embeddings ({len(embeddings)}).")

        name = collection_name or self.default_collection_name
        collection = self.get_or_create_collection(name)

        # ChromaDB requires string IDs. We'll generate them from file hash and chunk index.
        ids = [f"{chunk.metadata.get('file_hash', 'unknown')}-{chunk.metadata.get('chunk_index', '0')}" for chunk in chunks]
        
        # ChromaDB can't store complex objects in metadata, so we serialize it.
        # We only store primitives like str, int, float, bool.
        serializable_metadata = [
            {
                key: (str(value) if not isinstance(value, (str, int, float, bool)) else value)
                for key, value in chunk.metadata.items()
            }
            for chunk in chunks
        ]

        self._logger.info(f"Adding {len(chunks)} documents to collection '{name}'...")
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=serializable_metadata
        )
        self._logger.info("Successfully added documents to the collection.")
        return ids

    def query(self, query_vector: List[float], top_k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """
        Queries the vector store for the most similar document chunks.
        """
        collection = self.get_or_create_collection(self.default_collection_name)
        
        if not collection.count():
            self._logger.warning("Query attempted on an empty collection.")
            return []
            
        query_params = {
            "query_embeddings": [query_vector],
            "n_results": top_k
        }
        
        if metadata_filter:
            query_params["where"] = metadata_filter
            
        self._logger.info(f"Performing a similarity search for top {top_k} results...")
        results = collection.query(**query_params)
        self._logger.info(f"Found {len(results.get('ids', [[]])[0])} results.")

        retrieved_chunks = []
        # The result structure is complex and can be missing keys if no results are found.
        ids = results.get('ids', [[]])[0]
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]

        # Ensure all lists are valid and of the same length
        if not (ids and documents and metadatas and len(ids) == len(documents) == len(metadatas)):
            self._logger.warning("Query result components have mismatched lengths or are missing. Returning empty list.")
            return []

        for doc_id, text, meta in zip(ids, documents, metadatas):
            # We are not currently returning embeddings with the query result, so we can omit them here.
            retrieved_chunks.append(DocumentChunk(text=text, metadata=meta))

        return retrieved_chunks
    
    def count(self, collection_name: str) -> int:
        """Returns the number of chunks in the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        return collection.count()
            
    def stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Architecture: Collection introspection
        Strategy: Return comprehensive collection information
        """
        self._ensure_collection_initialized()
        
        try:
            count = self.count(self.default_collection_name) # Default collection for general stats
            
            stats = {
                "collection_name": self.default_collection_name,
                "total_chunks": count,
                "persist_directory": str(self.persist_directory),
                "collection_exists": True
            }
            
            self._logger.debug(f"Collection stats: {stats}")
            return stats
            
        except Exception as e:
            self._logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.default_collection_name,
                "total_chunks": 0,
                "persist_directory": str(self.persist_directory),
                "collection_exists": False,
                "error": str(e)
            }
    
    def clear(self) -> None:
        """
        Clears all documents from the collection. Used for testing.
        """
        try:
            self._client.delete_collection(self.default_collection_name)
            self._collection = None # Reset the collection object
            self._logger.info(f"Successfully deleted collection '{self.default_collection_name}'.")
        except Exception as e:
            self._logger.warning(f"Could not delete collection '{self.default_collection_name}', it may not have existed. Error: {e}")
    
    def persist(self) -> None:
        """
        Persist data to disk.
        
        Architecture: Data persistence
        Strategy: ChromaDB automatically persists, this is a no-op
        """
        # ChromaDB automatically persists data
        # This method exists for protocol compliance
        self._logger.debug("Data automatically persisted by ChromaDB")
