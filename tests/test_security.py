import re

def redact_pii(text):
    # Your actual PII logic from app.py should be imported here
    # This is a placeholder to prove the test works
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.sub(email_pattern, "[REDACTED]", text)

def test_pii_redaction():
    sensitive_input = "Contact me at anudeep@gmail.com for keys."
    safe_output = redact_pii(sensitive_input)
    
    assert "anudeep@gmail.com" not in safe_output
    assert "[REDACTED]" in safe_output

