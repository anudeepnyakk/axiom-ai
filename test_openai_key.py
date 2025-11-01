"""Test if OpenAI API key is valid"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {bool(api_key)}")
print(f"Key starts with: {api_key[:20] if api_key else 'NONE'}...")
print(f"Key length: {len(api_key) if api_key else 0}")

# Test with OpenAI SDK
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Simple test call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    
    print("\n✅ API KEY WORKS!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ API KEY FAILED: {e}")
    print(f"Error type: {type(e).__name__}")




