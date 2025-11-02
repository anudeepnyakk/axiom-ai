"""
LLM Synthesizer
This component is responsible for the "Generation" part of RAG.
It takes the user's query and the retrieved context chunks and generates
a final, coherent answer using a Large Language Model.
"""

import logging
from typing import List, Dict, Any, Protocol, Optional

import tiktoken

from axiom.core.interfaces import DocumentChunk, LLMProvider
from ..state_tracker import StateTracker
from axiom.retry_utils import AllRetriesFailed

# A reasonable budget to leave room for the query, prompt instructions, and response.
# (e.g., gpt-4 has an 8k context window, gpt-3.5-turbo has 4k)
TOKEN_BUDGET = 3000


class LLMSynthesizer:
    """
    Orchestrates the synthesis of the final answer using an LLM provider.
    """

    def __init__(self, provider: LLMProvider, state_tracker: Optional[StateTracker] = None):
        """
        Initializes the synthesizer with a specific LLM provider and optional state tracker.

        Args:
            provider: An object that conforms to the LLMProvider protocol.
            state_tracker: An optional StateTracker for conversation memory.
        """
        self.provider = provider
        self.state_tracker = state_tracker
        self.logger = logging.getLogger(__name__)
        # Initialize tokenizer for token budgeting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.logger.warning("Could not load tiktoken 'cl100k_base' encoding. Using basic split().")
            self.tokenizer = None
        
        self.logger.info(f"LLMSynthesizer initialized with provider: {provider.get_provider_info().get('provider_name', 'Unknown')}")

    def synthesize(self, query: str, context_chunks: List[DocumentChunk], session_id: Optional[str] = None) -> str:
        """
        Takes the query and context chunks and produces the final answer.

        This method performs three key steps:
        1.  Checks if there is sufficient context to answer the question.
        2.  Formats the context and query into a precise prompt for the LLM.
        3.  Calls the LLM provider to generate the final answer.
        4.  Records the interaction in the state tracker if available.
        """
        if not context_chunks:
            self.logger.warning("Synthesis attempted with no context chunks. Returning a default message.")
            return "There is not enough information in the provided documents to answer this question."

        # 1. Get conversation history if state tracking is enabled.
        history_string = ""
        if self.state_tracker and session_id:
            history = self.state_tracker.get_query_history(session_id)
            history_string = self._format_history_for_prompt(history)

        # 2. Format the context for the LLM prompt.
        # This is a critical step in prompt engineering. We create a clear, well-structured
        # block of text that the LLM can easily parse.
        context_string = self._format_context_for_prompt(context_chunks)

        # 3. Generate the final answer using the LLM provider (with retry logic).
        self.logger.info("Generating final answer using LLM...")
        
        try:
            final_answer = self.provider.generate_answer(
                query=query, 
                context=context_string,
                history=history_string
            )
            self.logger.info("Successfully generated final answer.")
            
        except AllRetriesFailed as e:
            # LLM service is unavailable - enter degraded mode
            self.logger.warning(f"LLM service failed after all retries. Entering degraded mode. Error: {e}")
            final_answer = self._generate_degraded_answer(query, context_chunks)
            self.logger.info("Generated degraded mode answer (retrieval-only)")

        # 4. Record the new Q&A in our history.
        if self.state_tracker and session_id:
            self.state_tracker.add_query_to_history(
                session_id=session_id,
                question=query,
                answer=final_answer
            )

        return final_answer

    def synthesize_for_insight(self, context_chunks: List[DocumentChunk]) -> str:
        """
        Synthesizes a novel insight from a collection of context chunks from different sources.
        This uses a different, more open-ended prompt than the standard Q&A synthesize.
        """
        if not context_chunks:
            self.logger.warning("Insight synthesis attempted with no context chunks.")
            return "Not enough information provided to synthesize an insight."

        context_string = self._format_context_for_prompt(context_chunks)
        
        # We use a special query/prompt for this synthesis task
        synthesis_query = (
            "Your task is to act as a research assistant. "
            "Analyze the provided text excerpts from different documents. "
            "Synthesize a novel insight, an interesting connection, a surprising contradiction, "
            "or a key theme that emerges from combining these sources. "
            "Present your finding as a concise, well-reasoned paragraph."
        )

        self.logger.info("Generating cross-document insight using LLM...")
        insight = self.provider.generate_answer(query=synthesis_query, context=context_string)
        self.logger.info("Successfully generated insight.")

        return insight

    def _format_context_for_prompt(self, chunks: List[DocumentChunk]) -> str:
        """
        Formats the list of DocumentChunk objects into a single string
        to be used as context in the LLM prompt, respecting a token budget.
        """
        prompt_context = []
        total_tokens = 0

        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get('source_file_path', 'Unknown Source')
            page = chunk.metadata.get('page_number', '')
            source_citation = f"Source {i} (File: {source}, Page: {page if page else 'N/A'}):"
            
            context_block = f"{source_citation}\n---\n{chunk.text}\n---"
            
            # Token budgeting
            if self.tokenizer:
                num_tokens = len(self.tokenizer.encode(context_block))
            else:
                num_tokens = len(context_block.split()) # Fallback

            if total_tokens + num_tokens > TOKEN_BUDGET:
                self.logger.warning(
                    f"Token budget reached. Stopping context at chunk {i-1}/{len(chunks)}."
                )
                break

            prompt_context.append(context_block)
            total_tokens += num_tokens
            
        return "\n\n".join(prompt_context)

    def _generate_degraded_answer(self, query: str, context_chunks: List[DocumentChunk]) -> str:
        """
        Generate a degraded mode answer when LLM service is unavailable.
        
        In degraded mode, we return the retrieved context chunks directly
        without LLM synthesis. This maintains partial functionality.
        
        Args:
            query: User's question
            context_chunks: Retrieved document chunks
            
        Returns:
            str: Degraded answer with context chunks
        """
        self.logger.info("Generating degraded mode response...")
        
        # Build a response showing the retrieved context
        response_parts = [
            "⚠️ **DEGRADED MODE**: The AI synthesis service is temporarily unavailable.",
            "",
            f"**Your Question**: {query}",
            "",
            "**Retrieved Document Excerpts** (unprocessed):",
            ""
        ]
        
        # Add each context chunk
        for i, chunk in enumerate(context_chunks[:5], 1):  # Limit to top 5
            source = chunk.metadata.get('source_file_path', 'Unknown source')
            response_parts.append(f"**Excerpt {i}** (from {source}):")
            response_parts.append(chunk.text[:500] + "..." if len(chunk.text) > 500 else chunk.text)
            response_parts.append("")
        
        response_parts.extend([
            "---",
            "",
            "💡 **Note**: These are raw document excerpts. Normal service will provide a synthesized answer.",
            "Please try again in a few moments or contact support if the issue persists."
        ])
        
        return "\n".join(response_parts)
    
    def _format_history_for_prompt(self, history: List[Dict[str, Any]]) -> str:
        """
        Formats the conversation history into a single string for the prompt.
        """
        if not history:
            return ""
        
        formatted_history = ["Previous conversation:"]
        for item in history:
            formatted_history.append(f"User: {item['question']}")
            formatted_history.append(f"Assistant: {item['answer']}")
        
        return "\n".join(formatted_history)
