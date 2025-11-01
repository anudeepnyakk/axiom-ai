"""
Query Engine - The Core RAG Brain

This module implements the QueryEngine that combines:
- Vector similarity search (retrieval)
- Context-aware answer generation
- Result ranking and filtering
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from axiom.core.interfaces import VectorStore, EmbeddingGenerator, DocumentChunk, QueryResult
from axiom.core.llm_synthesizer import LLMSynthesizer
from axiom.core.basic_chunker import BasicChunker
from axiom.metrics import REQUEST_COUNT, ERROR_COUNT, LATENCY_SECONDS
from axiom.request_context import request_context, get_request_id
from axiom.security import redact_pii, verify_api_key


class QueryEngine:
    """
    Core RAG Query Engine that combines retrieval and generation
    
    This is the brain of Project Axiom - it takes questions and returns
    intelligent answers based on your document knowledge base.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        llm_synthesizer: LLMSynthesizer,
        chunker: BasicChunker,
        max_context_chunks: int = 5,
        similarity_threshold: float = 0.7,
        require_auth: bool = False
    ):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.llm_synthesizer = llm_synthesizer
        self.chunker = chunker
        self.max_context_chunks = max_context_chunks
        self.similarity_threshold = similarity_threshold
        self.require_auth = require_auth
        self._logger = logging.getLogger(__name__)
        
        self._logger.info(
            "QueryEngine initialized",
            extra={
                "max_context_chunks": max_context_chunks,
                "similarity_threshold": similarity_threshold,
                "require_auth": require_auth
            }
        )
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        session_id: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> QueryResult:
        """
        Main query method - the heart of the RAG system
        
        Args:
            question: User's question
            top_k: Number of top results to retrieve
            session_id: Optional session ID for conversation memory
            api_key: Optional API key for authentication (required if require_auth=True)
            
        Returns:
            QueryResult with answer and context
        """
        # Use request context for ID correlation across stages
        with request_context() as request_id:
            REQUEST_COUNT.labels(stage='query').inc()
            with LATENCY_SECONDS.labels(stage='query').time():
                # Check authentication if required
                if self.require_auth and not verify_api_key(api_key):
                    ERROR_COUNT.labels(stage='auth').inc()
                    self._logger.warning("Authentication failed", extra={"request_id": request_id})
                    raise PermissionError("Invalid or missing API key")
                
                if not question.strip():
                    ERROR_COUNT.labels(stage='query').inc()
                    raise ValueError("Question cannot be empty")
                
                top_k = top_k or self.max_context_chunks
                
                # Redact PII from question before logging
                redacted_question = redact_pii(question)
                
                self._logger.info(
                    "Processing query",
                    extra={
                        "question": redacted_question[:100] + "..." if len(redacted_question) > 100 else redacted_question,
                        "top_k": top_k,
                        "request_id": request_id
                    }
                )
            
                try:
                    # Step 1: Generate embedding for the question
                    self._logger.info("Generating query embedding", extra={"stage": "embedding"})
                    question_embedding = self.embedding_generator.embed_batch([DocumentChunk(text=question, metadata={})])[0]

                    # Step 2: Search for relevant document chunks
                    self._logger.info("Searching vector store", extra={"stage": "retrieval", "top_k": top_k})
                    search_results = self.vector_store.query(
                        query_vector=question_embedding,
                        top_k=top_k
                    )
                    self._logger.info("Retrieved chunks", extra={"stage": "retrieval", "chunk_count": len(search_results)})

                    # Step 3: Generate the final answer
                    self._logger.info("Generating answer with LLM", extra={"stage": "llm"})
                    answer = self._generate_answer(question, search_results, session_id)

                    self._logger.info("Query completed successfully", extra={"request_id": request_id})
                    return QueryResult(
                        question=question,
                        answer=answer,
                        context_chunks=search_results
                    )

                except Exception as e:
                    ERROR_COUNT.labels(stage='query').inc()
                    self._logger.error("Query failed", extra={"error": str(e), "request_id": request_id}, exc_info=True)
                    # In case of failure, return a safe default
                    return QueryResult(
                        question=question,
                        answer="I am sorry, but an unexpected error occurred while processing your request.",
                        context_chunks=[]
                    )
    
    def synthesize_across_documents(self, source_file_paths: List[str], chunks_per_doc: int = 3) -> str:
        """
        Retrieves key chunks from multiple documents and synthesizes a novel insight.

        Args:
            source_file_paths: A list of the source_file_path metadata for the documents.
            chunks_per_doc: The number of key chunks to retrieve from each document.

        Returns:
            A string containing the synthesized insight.
        """
        self._logger.info(
            "Starting synthesis across documents",
            extra={"documents": source_file_paths, "chunks_per_doc": chunks_per_doc}
        )
        
        all_context_chunks = []
        
        # A generic query to find the most representative chunks
        generic_query = "What are the main themes, key arguments, and core concepts of this document?"
        query_embedding = self.embedding_generator.embed_batch([DocumentChunk(text=generic_query, metadata={})])[0]
        
        for file_path in source_file_paths:
            self._logger.debug(f"Retrieving key chunks for: {file_path}")
            # Use a metadata filter to scope the search to a single document
            metadata_filter = {"source_file_path": file_path}
            
            doc_chunks = self.vector_store.query(
                query_vector=query_embedding,
                top_k=chunks_per_doc,
                metadata_filter=metadata_filter
            )
            
            if doc_chunks:
                all_context_chunks.extend(doc_chunks)
                self._logger.debug(f"Found {len(doc_chunks)} chunks for {file_path}")
            else:
                self._logger.warning(f"Could not find any chunks for document: {file_path}")

        if not all_context_chunks:
            return "Could not retrieve enough information from the specified documents to synthesize an insight."
            
        # Call the new synthesizer method
        insight = self.llm_synthesizer.synthesize_for_insight(context_chunks=all_context_chunks)
        
        return insight

    def _generate_answer(
        self,
        question: str,
        context_chunks: List[DocumentChunk],
        session_id: Optional[str] = None
    ) -> str:
        """
        Generate answer using the LLMSynthesizer.
        
        This is where the magic happens - combining question + context
        to generate intelligent, relevant answers.
        """
        return self.llm_synthesizer.synthesize(
            query=question,
            context_chunks=context_chunks,
            session_id=session_id
        )
    
    def _combine_context_chunks(
        self,
        chunks: List[DocumentChunk]
    ) -> str:
        """Combine multiple context chunks into readable text"""
        combined = []
        
        for i, chunk in enumerate(chunks):
            source = chunk.metadata.get('source', f'Document {i+1}')
            combined.append(f"[{source}]: {chunk.text[:200]}...")
        
        return "\n\n".join(combined)
    
    def _calculate_confidence(
        self,
        context_chunks: List[DocumentChunk]
    ) -> float:
        """Calculate confidence score based on context quality"""
        if not context_chunks:
            return 0.0
        
        # Simple confidence calculation
        # In a real system, you'd use more sophisticated metrics
        base_confidence = min(len(context_chunks) / self.max_context_chunks, 1.0)
        
        # Boost confidence if we have multiple sources
        source_diversity = len(set(
            chunk.metadata.get('source', 'unknown') 
            for chunk in context_chunks
        ))
        diversity_boost = min(source_diversity / len(context_chunks), 0.2)
        
        return min(base_confidence + diversity_boost, 1.0)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and health information"""
        try:
            vector_store_stats = self.vector_store.stats()
            embedding_info = self.embedding_generator.get_model_info()
            
            return {
                "vector_store": vector_store_stats,
                "embedding_model": embedding_info,
                "query_engine": {
                    "max_context_chunks": self.max_context_chunks,
                    "similarity_threshold": self.similarity_threshold
                }
            }
        except Exception as e:
            self._logger.error(f"Failed to get system stats: {e}")
            return {"error": str(e)}
