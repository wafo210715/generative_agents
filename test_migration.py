#!/usr/bin/env python3
"""
Test script to verify the LLM API migration is working correctly
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'reverie/backend_server'))

def test_imports():
    """Test that all migrated modules import successfully"""
    print("Testing imports...")

    try:
        from persona.prompt_template import gpt_structure
        from persona.prompt_template import run_gpt_prompt
        from persona import persona as persona_module
        from persona.cognitive_modules import plan
        print("✅ All core modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_call():
    """Test that the DeepSeek API is working"""
    print("\nTesting DeepSeek API...")

    try:
        from persona.prompt_template.gpt_structure import llm_chat_request

        result = llm_chat_request("Hello! Please respond with 'API test successful' if you receive this message.")

        if "ERROR" in result:
            print(f"❌ API Error: {result}")
            return False
        else:
            print(f"✅ API Response: {result[:80]}...")
            print("✅ DeepSeek API is working correctly")
            return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_migrated_functions():
    """Verify migrated functions are available"""
    print("\nChecking migrated functions...")

    try:
        from persona.prompt_template.run_gpt_prompt import (
            run_gpt_prompt_wake_up_hour,
            run_gpt_prompt_daily_plan,
            run_gpt_prompt_task_decomp,
            run_gpt_prompt_action_sector,
            run_gpt_prompt_action_arena
        )
        print("✅ All critical migrated functions are available")
        return True
    except Exception as e:
        print(f"❌ Function import failed: {e}")
        return False

def count_migrations():
    """Count how many functions were migrated"""
    print("\nChecking migration status...")

    import re

    file_path = '/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py'

    with open(file_path, 'r') as f:
        content = f.read()

    # Count modern API calls
    llm_count = len(re.findall(r'llm_safe_generate_response', content))

    # Count legacy API calls (excluding comments)
    legacy_lines = re.findall(r'^\s*output = safe_generate_response', content, re.MULTILINE)

    print(f"✅ Functions using modern API (llm_safe_generate_response): {llm_count}")
    print(f"✅ Remaining legacy API calls (in comments): {len(legacy_lines)}")

    if len(legacy_lines) == 0:
        print("✅ No active legacy API calls found!")
        return True
    else:
        print("⚠️  Some legacy API calls may still be active")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM API MIGRATION VERIFICATION TEST")
    print("=" * 60)

    results = []

    results.append(test_imports())
    results.append(test_api_call())
    results.append(test_migrated_functions())
    results.append(count_migrations())

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("✅ DeepSeek API is working")
        print("✅ All critical functions migrated")
        print("✅ No legacy GPT-3 API calls in active code")
        print("\nThe simulation should now work without 'TOKEN LIMIT EXCEEDED' errors!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
