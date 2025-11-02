"""
API Key Authentication Module

Provides simple but secure API key authentication for Axiom endpoints.

Features:
- Environment variable-based API keys
- Multiple key support (for different clients/users)
- Constant-time comparison (prevents timing attacks)
- Configurable key prefixes for easy identification
"""

import os
import hmac
import hashlib
import logging
from typing import Optional, List, Set
from functools import wraps

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """Manages API key authentication."""
    
    def __init__(self, api_keys: Optional[List[str]] = None, env_var: str = "AXIOM_API_KEYS"):
        """
        Initialize API key authentication.
        
        Args:
            api_keys: List of valid API keys. If None, loads from environment variable.
            env_var: Environment variable name containing comma-separated API keys.
        """
        if api_keys is None:
            # Load from environment variable
            keys_str = os.getenv(env_var, "")
            if keys_str:
                self.valid_keys: Set[str] = set(k.strip() for k in keys_str.split(",") if k.strip())
            else:
                self.valid_keys = set()
                logger.warning(f"No API keys configured. Set {env_var} environment variable.")
        else:
            self.valid_keys = set(api_keys)
        
        if self.valid_keys:
            logger.info(f"APIKeyAuth initialized with {len(self.valid_keys)} key(s)")
        else:
            logger.warning("APIKeyAuth initialized with NO keys - authentication will fail!")
    
    def verify_key(self, provided_key: Optional[str]) -> bool:
        """
        Verify if the provided API key is valid.
        
        Uses constant-time comparison to prevent timing attacks.
        
        Args:
            provided_key: The API key to verify
            
        Returns:
            True if the key is valid, False otherwise
        """
        if not provided_key or not self.valid_keys:
            return False
        
        # Use constant-time comparison against all valid keys
        for valid_key in self.valid_keys:
            if self._secure_compare(provided_key, valid_key):
                return True
        
        return False
    
    @staticmethod
    def _secure_compare(a: str, b: str) -> bool:
        """
        Constant-time string comparison to prevent timing attacks.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            True if strings are equal
        """
        # Use HMAC for constant-time comparison
        # Both strings must be encoded to bytes
        a_bytes = a.encode('utf-8')
        b_bytes = b.encode('utf-8')
        return hmac.compare_digest(a_bytes, b_bytes)
    
    def require_api_key(self, func):
        """
        Decorator to require API key authentication for a function.
        
        Usage:
            @api_auth.require_api_key
            def my_protected_endpoint(api_key: str, ...):
                # API key is automatically validated
                pass
        """
        @wraps(func)
        def wrapper(*args, api_key: Optional[str] = None, **kwargs):
            if not self.verify_key(api_key):
                logger.warning("Authentication failed: Invalid or missing API key")
                raise PermissionError("Invalid or missing API key")
            
            logger.info("Authentication successful")
            return func(*args, **kwargs)
        
        return wrapper


class APIKeyGenerator:
    """Utility to generate secure API keys."""
    
    @staticmethod
    def generate(prefix: str = "axiom", length: int = 32) -> str:
        """
        Generate a secure random API key.
        
        Args:
            prefix: Key prefix for easy identification
            length: Length of the random part (in hex characters)
            
        Returns:
            Formatted API key like "axiom_1a2b3c4d..."
        """
        random_part = hashlib.sha256(os.urandom(32)).hexdigest()[:length]
        return f"{prefix}_{random_part}"


# Global instance (loaded from environment)
_default_auth = APIKeyAuth()


def verify_api_key(api_key: str) -> bool:
    """
    Convenience function to verify an API key using the default authenticator.
    
    Args:
        api_key: The API key to verify
        
    Returns:
        True if valid, False otherwise
    """
    return _default_auth.verify_key(api_key)


def require_api_key(func):
    """
    Convenience decorator using the default authenticator.
    
    Usage:
        from axiom.security import require_api_key
        
        @require_api_key
        def protected_function(api_key: str, ...):
            pass
    """
    return _default_auth.require_api_key(func)

