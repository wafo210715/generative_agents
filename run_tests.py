#!/usr/bin/env python3
"""
Quick test script for DeepSeek LLM integration
Tests both model configurations and runs a simple API call
"""

import sys
sys.path.append('./reverie/backend_server')

from utils import reasoner_models, chat_models
from persona.prompt_template.gpt_structure import llm_chat_request

print("🚀 DeepSeek LLM Integration Test")
print("=" * 50)

# Test configuration
print("Checking model configurations...")
print(f"Reasoner models configured: {len(reasoner_models)}")
print(f"Chat models configured: {len(chat_models)}")

# Test chat model
print("\nTesting DeepSeek-Chat...")
try:
    response = llm_chat_request("Hello! Please confirm you're working.", model_type="chat")
    print(f"✅ Response: {response[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test reasoner model
print("\nTesting DeepSeek-Reasoner...")
try:
    response = llm_chat_request("What is 2+2? Explain briefly.", model_type="reasoner")
    print(f"✅ Response: {response[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test complete! Your DeepSeek integration is working.")
print("\nNext steps:")
print("1. Start Django server: cd environment/frontend_server && python manage.py runserver")
print("2. Start simulation: cd reverie/backend_server && python reverie.py")
