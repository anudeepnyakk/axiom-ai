"""
PII Redaction Module

Automatically detects and redacts Personally Identifiable Information (PII)
from user inputs before logging or storing.

Supported PII types:
- Email addresses
- Phone numbers (US format)
- Social Security Numbers (US)
- Credit card numbers
- IP addresses (optional)
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PIIRedactor:
    """Redacts PII from text using regex patterns."""
    
    # Regex patterns for common PII types
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b|\b\d{3}-\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }
    
    # Replacement tokens
    REPLACEMENTS = {
        'email': '[EMAIL_REDACTED]',
        'phone': '[PHONE_REDACTED]',
        'ssn': '[SSN_REDACTED]',
        'credit_card': '[CARD_REDACTED]',
        'ip_address': '[IP_REDACTED]',
    }
    
    def __init__(self, redact_types: Optional[List[str]] = None):
        """
        Initialize the PII redactor.
        
        Args:
            redact_types: List of PII types to redact. If None, redacts all types
                         except IP addresses. Options: email, phone, ssn, credit_card, ip_address
        """
        if redact_types is None:
            # By default, redact everything except IP addresses
            self.redact_types = ['email', 'phone', 'ssn', 'credit_card']
        else:
            self.redact_types = redact_types
        
        # Compile patterns for efficiency
        self.compiled_patterns = {
            pii_type: re.compile(self.PATTERNS[pii_type])
            for pii_type in self.redact_types
            if pii_type in self.PATTERNS
        }
        
        logger.info(f"PIIRedactor initialized with types: {self.redact_types}")
    
    def redact(self, text: str) -> str:
        """
        Redact PII from the given text.
        
        Args:
            text: The input text that may contain PII
            
        Returns:
            Text with PII replaced by redaction tokens
        """
        if not text:
            return text
        
        redacted_text = text
        redactions_made = {}
        
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(redacted_text)
            if matches:
                redactions_made[pii_type] = len(matches) if isinstance(matches[0], str) else len(matches)
                redacted_text = pattern.sub(self.REPLACEMENTS[pii_type], redacted_text)
        
        if redactions_made:
            logger.info(f"PII redacted: {redactions_made}")
        
        return redacted_text
    
    def redact_dict(self, data: Dict) -> Dict:
        """
        Recursively redact PII from all string values in a dictionary.
        
        Args:
            data: Dictionary that may contain PII in values
            
        Returns:
            Dictionary with PII redacted from all string values
        """
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.redact(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    self.redact(item) if isinstance(item, str)
                    else self.redact_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                redacted[key] = value
        return redacted


# Global instance for convenience
_default_redactor = PIIRedactor()


def redact_pii(text: str) -> str:
    """
    Convenience function to redact PII using the default redactor.
    
    Args:
        text: The input text that may contain PII
        
    Returns:
        Text with PII replaced by redaction tokens
    """
    return _default_redactor.redact(text)

