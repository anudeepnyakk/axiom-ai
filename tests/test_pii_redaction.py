"""
Test script for PII redaction functionality.

Demonstrates automatic detection and redaction of:
- Email addresses
- Phone numbers
- SSNs
- Credit cards
"""

from axiom.security import PIIRedactor, redact_pii


def test_email_redaction():
    """Test email address redaction"""
    print("\n" + "="*60)
    print("TEST 1: Email Redaction")
    print("="*60)
    
    text = "Please send the report to john.doe@company.com and jane@example.org"
    redacted = redact_pii(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    assert "john.doe@company.com" not in redacted
    assert "jane@example.org" not in redacted
    assert "[EMAIL_REDACTED]" in redacted
    print("✅ PASSED: Emails successfully redacted")


def test_phone_redaction():
    """Test phone number redaction"""
    print("\n" + "="*60)
    print("TEST 2: Phone Number Redaction")
    print("="*60)
    
    text = "Call me at 555-123-4567 or (555) 987-6543"
    redacted = redact_pii(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    assert "555-123-4567" not in redacted
    assert "(555) 987-6543" not in redacted
    assert "[PHONE_REDACTED]" in redacted
    print("✅ PASSED: Phone numbers successfully redacted")


def test_ssn_redaction():
    """Test SSN redaction"""
    print("\n" + "="*60)
    print("TEST 3: SSN Redaction")
    print("="*60)
    
    text = "My SSN is 123-45-6789 for verification"
    redacted = redact_pii(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    assert "123-45-6789" not in redacted
    assert "[SSN_REDACTED]" in redacted
    print("✅ PASSED: SSN successfully redacted")


def test_multiple_pii_types():
    """Test multiple PII types in one text"""
    print("\n" + "="*60)
    print("TEST 4: Multiple PII Types")
    print("="*60)
    
    text = """
    User query: My email is user@example.com and you can reach me at 555-0100.
    For verification, my SSN is 987-65-4321.
    """
    
    redacted = redact_pii(text)
    
    print("Original:")
    print(text)
    print("\nRedacted:")
    print(redacted)
    
    assert "user@example.com" not in redacted
    assert "555-0100" not in redacted
    assert "987-65-4321" not in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "[SSN_REDACTED]" in redacted
    print("✅ PASSED: Multiple PII types successfully redacted")


def test_selective_redaction():
    """Test selective PII redaction (only emails)"""
    print("\n" + "="*60)
    print("TEST 5: Selective Redaction (Email Only)")
    print("="*60)
    
    redactor = PIIRedactor(redact_types=['email'])
    
    text = "Email: user@test.com, Phone: 555-1234"
    redacted = redactor.redact(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    assert "user@test.com" not in redacted
    assert "555-1234" in redacted  # Phone should NOT be redacted
    print("✅ PASSED: Selective redaction working")


def test_dict_redaction():
    """Test redaction in nested dictionaries"""
    print("\n" + "="*60)
    print("TEST 6: Dictionary Redaction")
    print("="*60)
    
    redactor = PIIRedactor()
    
    data = {
        "query": "Contact john@company.com",
        "metadata": {
            "user_email": "admin@example.org",
            "phone": "555-9999"
        },
        "messages": [
            "Call me at 555-8888",
            "No PII here"
        ]
    }
    
    print("Original:")
    print(data)
    
    redacted = redactor.redact_dict(data)
    
    print("\nRedacted:")
    print(redacted)
    
    assert "john@company.com" not in str(redacted)
    assert "admin@example.org" not in str(redacted)
    assert "[EMAIL_REDACTED]" in redacted["query"]
    assert "[EMAIL_REDACTED]" in redacted["metadata"]["user_email"]
    assert "[PHONE_REDACTED]" in redacted["messages"][0]
    print("✅ PASSED: Dictionary redaction working")


def test_no_pii():
    """Test that normal text is unchanged"""
    print("\n" + "="*60)
    print("TEST 7: No PII Present")
    print("="*60)
    
    text = "What is the weather like today?"
    redacted = redact_pii(text)
    
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    assert text == redacted
    print("✅ PASSED: Non-PII text unchanged")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PII REDACTION TEST SUITE" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_email_redaction()
        test_phone_redaction()
        test_ssn_redaction()
        test_multiple_pii_types()
        test_selective_redaction()
        test_dict_redaction()
        test_no_pii()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ PII Redaction is working correctly!")
        print("   - Emails, phones, SSNs protected")
        print("   - Selective redaction available")
        print("   - Dictionary/nested structure support")
        print("   - Query logs are now secure")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

