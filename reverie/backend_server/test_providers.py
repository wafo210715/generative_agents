#!/usr/bin/env python3
"""
Test script for LLM provider configuration and conversation generation
Tests that models can be enabled/disabled, API calls work, and generates test conversations
"""

import sys
sys.path.append('.')

from utils import reasoner_models, chat_models, embedding_models
from persona.prompt_template.gpt_structure import llm_chat_request

# Test conversation prompt from original test.py
CONVERSATION_TEST_PROMPT = """
---
Character 1: Maria Lopez is working on her physics degree and streaming games on Twitch to make some extra money. She visits Hobbs Cafe for studying and eating just about everyday.
Character 2: Klaus Mueller is writing a research paper on the effects of gentrification in low-income communities.

Past Context:
138 minutes ago, Maria Lopez and Klaus Mueller were already conversing about conversing about Maria's research paper mentioned by Klaus This context takes place after that conversation.

Current Context: Maria Lopez was attending her Physics class (preparing for the next lecture) when Maria Lopez saw Klaus Mueller in the middle of working on his research paper at the library (writing the introduction).
Maria Lopez is thinking of initating a conversation with Klaus Mueller.
Current Location: library in Oak Hill College

(This is what is in Maria Lopez's head: Maria Lopez should remember to follow up with Klaus Mueller about his thoughts on her research paper. Beyond this, Maria Lopez doesn't necessarily know anything more about Klaus Mueller)

(This is what is in Klaus Mueller's head: Klaus Mueller should remember to ask Maria Lopez about her research paper, as she found it interesting that he mentioned it. Beyond this, Klaus Mueller doesn't necessarily know anything more about Maria Lopez)

Here is their conversation.

Maria Lopez: "
---
Output the response to the prompt above in json. The output should be a list of list where the inner lists are in the form of ["<Name>", "<Utterance>"]. Output multiple utterances in ther conversation until the conversation comes to a natural conclusion.
Example output json:
{"output": "[["Jane Doe", "Hi!"], ["John Doe", "Hello there!"] ... ]"}
"""

def test_model_configurations():
    """Test that model configurations are set up correctly"""
    print("=== Testing Model Configurations ===\n")

    print("Reasoner Models:")
    for name, config in reasoner_models.items():
        status = "✅ ENABLED" if config.get("is_valid") else "❌ DISABLED"
        print(f"  {name}: {status}")
        print(f"    - Model ID: {config['model_id']}")
        print(f"    - API Base: {config['api_base_url']}")
        print(f"    - Key set: {'Yes' if config['api_key'] != '<YOUR_API_KEY>' else 'No (placeholder)'}")
        print()

    print("Chat Models:")
    for name, config in chat_models.items():
        status = "✅ ENABLED" if config.get("is_valid") else "❌ DISABLED"
        print(f"  {name}: {status}")
        print(f"    - Model ID: {config['model_id']}")
        print(f"    - API Base: {config['api_base_url']}")
        print(f"    - Key set: {'Yes' if config['api_key'] != '<YOUR_API_KEY>' else 'No (placeholder)'}")
        print()

    print("Embedding Models:")
    for name, config in embedding_models.items():
        status = "✅ ENABLED" if config.get("is_valid") else "❌ DISABLED"
        print(f"  {name}: {status}")
        print(f"    - Model ID: {config['model_id']}")
        print(f"    - API Base: {config['api_base_url']}")
        print(f"    - Key set: {'Yes' if config['api_key'] != '<YOUR_API_KEY>' else 'No (placeholder)'}")
        print()

def test_api_call():
    """Test making an actual API call with the enabled models"""
    print("\n=== Testing API Call ===\n")

    test_prompt = "Hello! Please respond with 'API test successful' if you receive this message."

    print("Testing chat model...")
    try:
        response = llm_chat_request(test_prompt, model_type="chat")
        print(f"Response: {response}\n")

        if "ERROR" in response:
            print("❌ API call failed. Check your API key and configuration.")
        else:
            print("✅ API call successful!")

    except Exception as e:
        print(f"❌ Exception during API call: {e}")
        print("Make sure you have set a valid API key in utils.py")

    print("\nTesting reasoner model...")
    try:
        reasoning_prompt = "Explain the concept of artificial general intelligence in 2-3 sentences."
        response = llm_chat_request(reasoning_prompt, model_type="reasoner")
        print(f"Response: {response[:100]}...\n")

        if "ERROR" in response:
            print("❌ Reasoner API call failed.")
        else:
            print("✅ Reasoner API call successful!")

    except Exception as e:
        print(f"❌ Exception during reasoner API call: {e}")

def test_conversation_generation():
    """Test conversation generation using the test prompt from original test.py"""
    print("\n=== Testing Conversation Generation ===\n")

    print("Testing conversation generation with chat model...")
    print("Prompt: Maria and Klaus conversation about research papers\n")

    try:
        response = llm_chat_request(CONVERSATION_TEST_PROMPT, model_type="chat")
        print(f"Response:\n{response}\n")

        if "ERROR" in response:
            print("❌ Conversation generation failed.")
        else:
            print("✅ Conversation generation successful!")
            print("\nNote: Check if the output is valid JSON format")
            print("Expected format: [[\"Name\", \"Utterance\"], ...]")

    except Exception as e:
        print(f"❌ Exception during conversation generation: {e}")

    print("\nTesting reasoning task...")
    try:
        reasoning_prompt = """
        Reflect on the following: Maria is a physics student who streams games on Twitch.
        Klaus is writing about gentrification. They met at the library.
        What might be a natural topic for them to discuss?
        """
        response = llm_chat_request(reasoning_prompt, model_type="reasoner")
        print(f"Reasoning Response:\n{response[:200]}...\n")

        if "ERROR" in response:
            print("❌ Reasoning task failed.")
        else:
            print("✅ Reasoning task successful!")

    except Exception as e:
        print(f"❌ Exception during reasoning: {e}")

if __name__ == "__main__":
    print("LLM Provider Configuration Test")
    print("=" * 40)

    test_model_configurations()
    test_api_call()
    test_conversation_generation()

    print("\n" + "=" * 40)
    print("Test complete!")
    print("\nTo run the actual simulation:")
    print("1. Make sure at least one model is enabled (is_valid: True)")
    print("2. Set a valid API key for that model")
    print("3. Run: python reverie.py")
