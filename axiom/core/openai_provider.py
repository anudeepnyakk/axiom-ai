"""
OpenAI Provider
An implementation of the LLMProvider protocol that uses the OpenAI API
for generating answers. This is a key component for enabling the "Generation"
part of our RAG system with a powerful, cloud-based LLM.
"""

import logging
import os
from typing import Dict, Any, Optional

# It's good practice to check for the library's existence and provide a helpful error.
try:
    from openai import OpenAI
    from openai import OpenAIError, APIError, APIConnectionError, RateLimitError, APITimeoutError
except ImportError:
    raise ImportError("The 'openai' library is required to use the OpenAIProvider. Please install it with 'pip install openai'.")

from .interfaces import LLMProvider
from axiom.retry_utils import retry, AllRetriesFailed

# --- Constants for Prompt Engineering ---
# This is a critical part of building a reliable RAG system. The prompt is our contract
# with the LLM, instructing it precisely how to behave.

# This is the main system prompt that sets the LLM's persona and core instructions.
# It enforces our key requirement: "Answer ONLY from the provided sources."
SYSTEM_PROMPT = """
You are "Axiom," a sovereign AI assistant. Your purpose is to answer questions with precision and clarity, based exclusively on the provided context.

Follow these rules strictly:
1.  **Analyze the user's query and the provided text sources.**
2.  **Synthesize a comprehensive, standalone answer.** The answer should be self-contained and well-structured.
3.  **Base your answer ONLY on the information within the provided sources.** Do not use any external knowledge or prior training.
4.  **CRITICAL: Add inline source citations.** After each factual statement, add [S1], [S2], [S3] etc. to indicate which source it came from. For example: "Facebook embraced rapid iteration [S1]. The platform leveraged network effects to drive growth [S2]."
5.  **If the sources do not contain enough information to answer the question, you MUST state:** "There is not enough information in the provided documents to answer this question." Do not attempt to guess or infer an answer.
6.  **Do not mention sources in prose (e.g., "According to Source 1...").** Use only the [S1] citation format.
7.  **Your tone should be that of a precise, analytical, and trustworthy expert.**
"""

# This is the template for the user's message, which will contain the actual query and context.
# We use placeholders for the context and query that will be filled in at runtime.
USER_PROMPT_TEMPLATE = """{history_section}
**Context from Documents:**
---
{context}
---

**User Query:**
{query}

Based *only* on the context provided above, provide a comprehensive answer with inline citations [S1], [S2], etc. after each fact.
"""


class OpenAIProvider(LLMProvider):
    """
    An LLMProvider that connects to the OpenAI API.
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initializes the OpenAI client.

        Args:
            api_key: The OpenAI API key. It is crucial to handle this securely,
                     typically via environment variables, not hardcoded.
            model: The specific OpenAI model to use for generation.
        """
        if not api_key:
            # Fail-fast if the API key is missing. This prevents runtime errors.
            raise ValueError("OpenAI API key is required but was not provided.")
            
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OpenAIProvider initialized with model: {self.model}")

    @retry(
        max_attempts=3,
        backoff_base=1.0,
        exceptions=(APIError, APIConnectionError, RateLimitError, APITimeoutError)
    )
    def _make_api_call(self, messages: list, stream: bool = False):
        """
        Internal method that makes the actual OpenAI API call with retry logic.
        
        This is wrapped with @retry decorator to handle transient failures like:
        - Network timeouts
        - Rate limits
        - Temporary server errors
        
        Args:
            messages: List of message dicts for the chat completion
            stream: If True, returns a generator for streaming responses
            
        Returns:
            str or generator: Generated answer from OpenAI
            
        Raises:
            AllRetriesFailed: If all retry attempts are exhausted
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0,  # Deterministic, factual answers
            max_tokens=1024,  # Limit response length
            stream=stream
        )
        
        if stream:
            # Return generator for streaming
            return response
        else:
            # Extract the content from the first choice
            return response.choices[0].message.content.strip()
    
    def generate_answer(self, query: str, context: str, history: Optional[str] = None) -> str:
        """
        Generates an answer using the OpenAI Chat Completions API.
        
        Features fault tolerance with:
        - Automatic retry with exponential backoff (up to 3 attempts)
        - Retry on transient errors (timeouts, rate limits, server errors)
        - No retry on permanent errors (invalid API key, bad request)
        
        Args:
            query: User's question
            context: Retrieved document chunks
            history: Optional conversation history
            
        Returns:
            str: Generated answer
            
        Raises:
            AllRetriesFailed: If all retry attempts fail
            RuntimeError: For non-retryable errors
        """
        try:
            self.logger.info("Sending request to OpenAI API...")
            
            # Conditionally construct the history section for the prompt
            history_section = ""
            if history:
                history_section = f"**Previous Conversation History:**\n---\n{history}\n---\n\n"
            
            # Construct the conversation messages
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                    history_section=history_section,
                    context=context, 
                    query=query
                )}
            ]
            
            # Make the API call with retry logic
            generated_answer = self._make_api_call(messages)
            
            self.logger.info("Successfully received and parsed response from OpenAI API.")
            return generated_answer

        except AllRetriesFailed as e:
            # All retries exhausted - propagate for degraded mode handling
            self.logger.error(f"All retry attempts failed: {e}", exc_info=True)
            raise
            
        except Exception as e:
            # Non-retryable error (e.g., invalid API key, bad request)
            self.logger.error(f"Non-retryable error with OpenAI API: {e}", exc_info=True)
            raise RuntimeError("Failed to generate an answer due to an API error.") from e

    def generate_answer_stream(self, query: str, context: str, history: Optional[str] = None):
        """
        Generates an answer using streaming for better UX.
        
        Args:
            query: User's question
            context: Retrieved document chunks
            history: Optional conversation history
            
        Yields:
            str: Chunks of the generated answer as they arrive
        """
        try:
            self.logger.info("Sending streaming request to OpenAI API...")
            
            # Conditionally construct the history section
            history_section = ""
            if history:
                history_section = f"**Previous Conversation History:**\n---\n{history}\n---\n\n"
            
            # Construct the conversation messages
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                    history_section=history_section,
                    context=context, 
                    query=query
                )}
            ]
            
            # Make streaming API call
            stream = self._make_api_call(messages, stream=True)
            
            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
            
            self.logger.info("Successfully completed streaming response")
            
        except Exception as e:
            self.logger.error(f"Error in streaming: {e}", exc_info=True)
            yield "Error generating response. Please try again."
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Returns information about this provider.
        """
        return {
            "provider_name": "openai",
            "model_name": self.model
        }

def get_openai_provider_from_env() -> OpenAIProvider:
    """
    A convenience factory function to create an OpenAIProvider using an
    environment variable for the API key. This is the recommended way to
    instantiate the provider to avoid hardcoding credentials.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("The 'OPENAI_API_KEY' environment variable is not set. Please set it to your OpenAI API key.")
    return OpenAIProvider(api_key=api_key)
