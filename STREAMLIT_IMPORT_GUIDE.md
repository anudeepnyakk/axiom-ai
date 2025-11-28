# Streamlit Import Safety Guide

## The Problem

Streamlit reloads modules on every rerun. If you import packages that:
- Register global state (Prometheus metrics, singletons, etc.)
- Initialize heavy resources on import
- Have circular dependencies

You'll get errors like:
```
ValueError: Duplicated timeseries in CollectorRegistry
```

## The Solution: "Standalone Functions" Pattern

### ✅ DO THIS (Safe)
```python
# Standalone function - no heavy imports
import re

def redact_pii(text: str) -> str:
    """Simple regex-based redaction."""
    text = re.sub(r'pattern', '[REDACTED]', text)
    return text
```

### ❌ DON'T DO THIS (Risky)
```python
# Importing from complex package triggers initialization
from axiom.security.pii_redactor import redact_pii  # ❌ May trigger Prometheus registration
```

## When to Use Standalone Functions

Use standalone implementations when:
1. **The function is simple** (regex, string manipulation, basic math)
2. **The package has heavy initialization** (metrics, databases, global state)
3. **You only need one small feature** from a large package

## When It's Safe to Import

It's safe to import when:
- ✅ The package is **stateless** (pure functions)
- ✅ The package is **designed for Streamlit** (streamlit-*, langchain-*)
- ✅ The package **lazy-loads** resources (only initializes when called, not on import)

## Examples of Safe Imports in This Project

```python
# ✅ Safe - LangChain is designed for this
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# ✅ Safe - Standard library
import re
import os
import tempfile

# ✅ Safe - Streamlit packages
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
```

## Examples of Risky Imports (Avoid)

```python
# ❌ Risky - May have global state
from axiom.security.pii_redactor import redact_pii

# ❌ Risky - May initialize database on import
from some_package import DatabaseConnection

# ❌ Risky - May register metrics on import
from monitoring import register_metrics
```

## Quick Checklist Before Adding New Imports

- [ ] Does the package initialize anything on import? (Check `__init__.py`)
- [ ] Does it register global state (metrics, caches, connections)?
- [ ] Is the function I need simple enough to reimplement?
- [ ] Can I use `@st.cache_resource` to prevent re-initialization?

## If You Hit This Error Again

1. **Identify the problematic import** (check the traceback)
2. **Check if the function is simple** (regex, string ops, basic logic)
3. **Extract it as a standalone function** (copy the logic, not the import)
4. **Add a comment explaining why** (so future you knows)

## Current Standalone Functions in app.py

- `redact_pii()` - PII redaction (avoids Prometheus metrics registration)

