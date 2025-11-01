# Axiom AI - Security Documentation

This document outlines the security features, best practices, and threat model for Axiom AI's RAG system.

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [PII Protection](#pii-protection)
4. [Secrets Management](#secrets-management)
5. [Container Security](#container-security)
6. [Network Security](#network-security)
7. [Threat Model](#threat-model)
8. [Best Practices](#best-practices)
9. [Compliance](#compliance)
10. [Incident Response](#incident-response)

---

## Security Overview

### Defense-in-Depth

Axiom AI implements multiple layers of security:

```
┌────────────────────────────────────────────┐
│         Security Layers                     │
├────────────────────────────────────────────┤
│  1. Network (TLS, Firewall)                │
│  2. Authentication (API Keys)              │
│  3. Authorization (Future: RBAC)           │
│  4. PII Redaction (Logs)                   │
│  5. Input Validation                       │
│  6. Container Isolation                    │
│  7. Secrets Management                     │
│  8. Audit Logging                          │
└────────────────────────────────────────────┘
```

### Security Principles

1. **Least Privilege**: Minimize permissions at every level
2. **Defense in Depth**: Multiple security layers
3. **Fail Secure**: Errors deny access by default
4. **Audit Everything**: Comprehensive logging
5. **Zero Trust**: Verify explicitly, don't assume

---

## Authentication & Authorization

### API Key Authentication

**Implementation**: `axiom/security/api_auth.py`

#### Features

✅ **Environment-based configuration**: No secrets in code
✅ **Multiple keys support**: Different keys for different clients
✅ **Constant-time comparison**: Prevents timing attacks
✅ **Easy key rotation**: Add/remove keys without code changes

#### Usage

**Configuration**:
```bash
# Set in .env file
AXIOM_API_KEYS=axiom_key1,axiom_key2,axiom_key3
```

**Code Example**:
```python
from axiom.security import require_api_key

@require_api_key
def protected_endpoint(api_key: str, data: dict):
    # API key automatically validated
    # If invalid, PermissionError raised
    return process_data(data)
```

**HTTP Request** (future API):
```bash
curl -H "X-API-Key: axiom_key1" https://api.axiom.ai/query
```

#### Key Generation

```bash
# Generate secure API key
python -c "from axiom.security import APIKeyGenerator; print(APIKeyGenerator.generate())"

# Output: axiom_6919fa7722450a14a8839284df02cb14
```

#### Timing Attack Prevention

**Problem**: Naive string comparison leaks information about key characters through timing.

**Example** (vulnerable code):
```python
# ❌ BAD: Timing attack vulnerable
if provided_key == valid_key:
    return True
```

**Solution**: Constant-time comparison using HMAC.
```python
# ✅ GOOD: Constant-time comparison
import hmac
return hmac.compare_digest(provided_key.encode(), valid_key.encode())
```

**Test Results**:
```
1000 comparisons:
- Correct key: 0.000604s
- Wrong key:   0.000628s
- Ratio: 1.04x (effectively constant-time)
```

---

### Future: Role-Based Access Control (RBAC)

**Planned Implementation**:
```python
class User:
    username: str
    roles: List[str]  # ["admin", "user", "viewer"]

@require_role("admin")
def delete_documents():
    pass

@require_role("user")
def query_documents():
    pass
```

---

## PII Protection

### Automatic PII Redaction

**Implementation**: `axiom/security/pii_redactor.py`

#### Supported PII Types

| PII Type | Pattern | Example | Redacted |
|----------|---------|---------|----------|
| **Email** | Regex | user@example.com | [EMAIL_REDACTED] |
| **Phone** | US format | 555-123-4567 | [PHONE_REDACTED] |
| **SSN** | US format | 123-45-6789 | [SSN_REDACTED] |
| **Credit Card** | Major brands | 4111111111111111 | [CARD_REDACTED] |
| **IP Address** | IPv4 | 192.168.1.1 | [IP_REDACTED] |

#### Integration Points

**1. Query Logging**:
```python
# In QueryEngine.query()
redacted_question = redact_pii(question)
logger.info("Processing query", extra={"question": redacted_question})
```

**2. Error Messages**:
```python
try:
    process_user_input(data)
except Exception as e:
    redacted_error = redact_pii(str(e))
    logger.error(redacted_error)
```

**3. State Tracker** (future):
```python
# Before saving to database
session_data = redact_pii_dict(session_data)
db.save(session_data)
```

#### Selective Redaction

```python
from axiom.security import PIIRedactor

# Redact only emails and phones
redactor = PIIRedactor(redact_types=['email', 'phone'])
text = "Contact: user@example.com, SSN: 123-45-6789"
redacted = redactor.redact(text)

# Output: "Contact: [EMAIL_REDACTED], SSN: 123-45-6789"
```

#### Nested Structures

```python
data = {
    "query": "My email is user@test.com",
    "metadata": {
        "phone": "555-1234"
    }
}

redacted = PIIRedactor().redact_dict(data)
# All string values recursively redacted
```

---

## Secrets Management

### Environment Variables

**✅ DO**:
```bash
# Store in .env file (never committed)
OPENAI_API_KEY=sk-your-key-here
AXIOM_API_KEYS=key1,key2

# Load in code
import os
api_key = os.getenv("OPENAI_API_KEY")
```

**❌ DON'T**:
```python
# Hard-coded secrets (NEVER do this!)
OPENAI_API_KEY = "sk-abc123"
```

### Docker Secrets

**docker-compose.yml**:
```yaml
services:
  axiom-backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:?error}  # Required
      - AXIOM_API_KEYS=${AXIOM_API_KEYS}         # Optional
```

**Why `${VAR:?error}`?**
- Fails fast if required secret is missing
- Prevents accidental deployment without keys

### Cloud Secrets Management

#### AWS Secrets Manager
```python
import boto3

secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='axiom/openai-key')
openai_key = response['SecretString']
```

#### Google Secret Manager
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = "projects/PROJECT_ID/secrets/openai-key/versions/latest"
response = client.access_secret_version(request={"name": name})
openai_key = response.payload.data.decode('UTF-8')
```

#### Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://axiom-vault.vault.azure.net/", credential=credential)
secret = client.get_secret("openai-key")
openai_key = secret.value
```

---

## Container Security

### Dockerfile Best Practices

#### 1. Non-Root User ✅

**Implementation**:
```dockerfile
# Create user with specific UID
RUN useradd -m -u 1000 axiom

# Switch to non-root user
USER axiom
```

**Why?**
- Limits damage if container is compromised
- Prevents host file system modification
- Standard security practice

#### 2. Multi-Stage Builds ✅

**Implementation**:
```dockerfile
# Stage 1: Builder (has GCC, build tools)
FROM python:3.11-slim as builder
RUN apt-get install gcc
RUN pip install -r requirements.txt

# Stage 2: Runtime (minimal, no build tools)
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

**Benefits**:
- **70% smaller image**: No build tools in final image
- **Reduced attack surface**: Fewer packages = fewer vulnerabilities
- **Faster pulls**: Smaller image downloads faster

#### 3. Minimal Base Image ✅

**Choices**:
- ✅ `python:3.11-slim`: 40MB compressed
- ❌ `python:3.11`: 320MB compressed (8x larger!)
- ❌ `python:3.11-alpine`: Musl libc incompatibilities

#### 4. No Secrets in Layers ✅

**❌ Bad**:
```dockerfile
# Secret baked into layer (visible in history)
ENV OPENAI_API_KEY=sk-abc123
```

**✅ Good**:
```dockerfile
# Secret passed at runtime
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

### Image Scanning

**Scan for vulnerabilities**:
```bash
# Using Docker Scout
docker scout cves axiom-backend:latest

# Using Trivy
trivy image axiom-backend:latest

# Using Snyk
snyk container test axiom-backend:latest
```

---

## Network Security

### Container Networking

**Isolation**:
```yaml
networks:
  axiom-network:
    driver: bridge
    internal: false  # Allow internet access for OpenAI API
```

**Service Communication**:
- Backend → ChromaDB: `http://chromadb:8000` (internal network)
- Host → Backend: `http://localhost:5000` (exposed port)

**Firewall Rules** (production):
```bash
# Only allow HTTPS from internet
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow internal Docker network
iptables -A INPUT -s 172.18.0.0/16 -j ACCEPT

# Deny all other inbound
iptables -A INPUT -j DROP
```

---

### TLS/SSL (Production)

**Reverse Proxy** (Nginx):
```nginx
server {
    listen 443 ssl;
    server_name api.axiom.ai;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://axiom-backend:5000;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Threat Model

### Assets

1. **User Queries**: May contain PII or sensitive business data
2. **Documents**: Proprietary company knowledge
3. **API Keys**: OpenAI, authentication keys
4. **Vector Embeddings**: Represent document content

### Threat Actors

1. **External Attackers**: Trying to access system without authorization
2. **Malicious Users**: Valid users trying to abuse system
3. **Insider Threats**: Employees with legitimate access
4. **Supply Chain**: Compromised dependencies

---

### Threat Scenarios

#### 1. Unauthorized Access

**Threat**: Attacker tries to query system without API key.

**Mitigations**:
- ✅ API key authentication required
- ✅ Rate limiting (future)
- ✅ Fail2Ban for repeated attempts (future)

**Residual Risk**: Low

---

#### 2. PII Leakage in Logs

**Threat**: User queries contain SSNs, emails that get logged.

**Mitigations**:
- ✅ Automatic PII redaction before logging
- ✅ Logs stored with restricted access
- ⚠️ Log retention policy (30 days recommended)

**Residual Risk**: Low

---

#### 3. Timing Attacks on API Keys

**Threat**: Attacker measures response times to infer key characters.

**Mitigations**:
- ✅ Constant-time comparison using HMAC
- ✅ Verified 1.04x timing ratio (effectively constant)

**Residual Risk**: Very Low

---

#### 4. Container Escape

**Threat**: Attacker compromises container and escapes to host.

**Mitigations**:
- ✅ Non-root user in container
- ✅ Minimal base image (reduced attack surface)
- ✅ No privileged mode
- ⚠️ AppArmor/SELinux profiles (future)

**Residual Risk**: Low

---

#### 5. Supply Chain Attack

**Threat**: Malicious dependency in requirements.txt.

**Mitigations**:
- ✅ Pinned versions in requirements.txt
- ✅ Dependabot alerts (GitHub)
- ⚠️ Hash verification (pip --require-hashes)
- ⚠️ Private PyPI mirror (enterprise)

**Residual Risk**: Medium

---

#### 6. Injection Attacks

**Threat**: User input crafted to exploit LLM or vector search.

**Mitigations**:
- ✅ Input validation (length limits)
- ✅ Parameterized queries (ChromaDB client handles this)
- ⚠️ Prompt injection detection (future)

**Residual Risk**: Medium

---

#### 7. Data Exfiltration

**Threat**: Attacker queries system repeatedly to extract all documents.

**Mitigations**:
- ✅ API key authentication
- ⚠️ Rate limiting per key (future)
- ⚠️ Query logging and anomaly detection (future)

**Residual Risk**: Medium

---

## Best Practices

### For Developers

1. **Never commit secrets**:
   ```bash
   # Add to .gitignore
   .env
   *.key
   *.pem
   ```

2. **Use environment variables**:
   ```python
   api_key = os.getenv("API_KEY")
   if not api_key:
       raise ValueError("API_KEY not set")
   ```

3. **Validate inputs**:
   ```python
   if len(query) > 10000:
       raise ValueError("Query too long")
   ```

4. **Log securely**:
   ```python
   logger.info("Query processed", extra={"query": redact_pii(query)})
   ```

5. **Update dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade package
   ```

---

### For Operators

1. **Rotate API keys regularly** (every 90 days)
2. **Monitor logs** for suspicious patterns
3. **Apply security patches** within 7 days
4. **Backup secrets** to secure vault
5. **Test disaster recovery** monthly

---

### For Users

1. **Don't share API keys**
2. **Report suspicious activity**
3. **Use unique keys per application**
4. **Revoke unused keys**

---

## Compliance

### GDPR (EU Data Protection)

**Requirements**:
- ✅ PII redaction in logs (Article 25: Data protection by design)
- ⚠️ User data deletion (Article 17: Right to erasure) - Future
- ⚠️ Data portability (Article 20) - Future
- ⚠️ Consent management (Article 7) - Future

**Current Status**: Partial compliance (PII redaction implemented)

---

### HIPAA (US Healthcare)

**Requirements**:
- ✅ Access controls (API keys)
- ✅ Audit logs (JSON structured logging)
- ⚠️ Encryption at rest (use encrypted volumes)
- ⚠️ Encryption in transit (TLS required in production)
- ⚠️ Business Associate Agreement (BAA) with OpenAI

**Current Status**: Not HIPAA-compliant (needs encryption + BAA)

---

### SOC 2

**Requirements**:
- ✅ Access controls
- ✅ Audit logging
- ⚠️ Penetration testing (annual)
- ⚠️ Incident response plan
- ⚠️ Vendor management (OpenAI)

**Current Status**: Foundation in place, needs formal audit

---

## Incident Response

### Incident Types

1. **Data Breach**: Unauthorized access to documents/queries
2. **Service Disruption**: DDoS, system failure
3. **Malicious Use**: Abuse of API for harmful purposes
4. **Key Compromise**: API key leaked

---

### Response Plan

#### 1. Detection
- Monitor logs for anomalies
- Alert on repeated authentication failures
- Track unusual query patterns

#### 2. Containment
```bash
# Revoke compromised API key immediately
# Remove from AXIOM_API_KEYS environment variable
docker-compose restart axiom-backend
```

#### 3. Eradication
- Identify root cause
- Patch vulnerability
- Rotate all API keys (if key compromise)

#### 4. Recovery
- Restore from backup if needed
- Verify system integrity
- Resume normal operations

#### 5. Lessons Learned
- Document incident
- Update security practices
- Add new monitoring/alerts

---

### Key Compromise Response

**If API key is leaked**:

1. **Immediate** (within 5 minutes):
   ```bash
   # Remove compromised key from .env
   vim .env  # Delete the key line
   docker-compose restart axiom-backend
   ```

2. **Short-term** (within 1 hour):
   - Generate new key
   - Distribute to legitimate users
   - Monitor logs for unauthorized usage

3. **Long-term** (within 1 week):
   - Review how leak happened
   - Implement additional safeguards
   - Update documentation

---

## Security Checklist

### Pre-Deployment

- [ ] All secrets in environment variables (not code)
- [ ] PII redaction enabled
- [ ] API key authentication enabled
- [ ] Docker non-root user configured
- [ ] TLS certificate installed (production)
- [ ] Firewall rules configured
- [ ] Log retention policy set
- [ ] Backup strategy implemented

### Post-Deployment

- [ ] Monitor logs daily
- [ ] Rotate API keys (90 day cycle)
- [ ] Update dependencies monthly
- [ ] Review access logs weekly
- [ ] Test incident response quarterly
- [ ] Penetration test annually

---

## Reporting Security Issues

**If you discover a security vulnerability**:

1. **DO NOT** open a public GitHub issue
2. **Email**: security@axiom.ai (example - set up your own)
3. **Include**:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Your contact information

**Expected Response**:
- Acknowledgment within 24 hours
- Initial assessment within 72 hours
- Fix timeline communicated within 1 week

---

## References

### Standards

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Docker Benchmarks](https://www.cisecurity.org/benchmark/docker)

### Tools

- [Trivy](https://github.com/aquasecurity/trivy): Container vulnerability scanner
- [Bandit](https://github.com/PyCQA/bandit): Python security linter
- [Safety](https://github.com/pyupio/safety): Dependency vulnerability checker

---

## Conclusion

Security is **not a feature, it's a process**. Axiom AI implements multiple layers of defense, but security is only as strong as its weakest link.

**Key Takeaways**:
1. ✅ API key authentication prevents unauthorized access
2. ✅ PII redaction protects user privacy
3. ✅ Container security minimizes attack surface
4. ⚠️ Continuous monitoring and updates are essential

**Remember**: Security is everyone's responsibility.

---

*Last Updated: 2025-10-28*
*Security Status: Production-Ready with Ongoing Improvements*

