#!/usr/bin/env python3
"""
Test script for refactored run_gpt_prompt.py
Tests all 32 prompt functions for correct imports and basic functionality
"""

import sys
import os

# Add paths to import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

def test_imports():
    """Test that all functions can be imported"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)

    try:
        from persona.prompt_template.run_gpt_prompt import (
            run_gpt_prompt_wake_up_hour,
            run_gpt_prompt_daily_plan,
            run_gpt_prompt_generate_hourly_schedule,
            run_gpt_prompt_task_decomp,
            run_gpt_prompt_action_sector,
            run_gpt_prompt_action_arena,
            run_gpt_prompt_action_game_object,
            run_gpt_prompt_pronunciatio,
            run_gpt_prompt_event_triple,
            run_gpt_prompt_act_obj_desc,
            run_gpt_prompt_act_obj_event_triple,
            run_gpt_prompt_new_decomp_schedule,
            run_gpt_prompt_decide_to_talk,
            run_gpt_prompt_decide_to_react,
            run_gpt_prompt_create_conversation,
            run_gpt_prompt_summarize_conversation,
            run_gpt_prompt_extract_keywords,
            run_gpt_prompt_keyword_to_thoughts,
            run_gpt_prompt_convo_to_thoughts,
            run_gpt_prompt_event_poignancy,
            run_gpt_prompt_thought_poignancy,
            run_gpt_prompt_chat_poignancy,
            run_gpt_prompt_focal_pt,
            run_gpt_prompt_insight_and_guidance,
            run_gpt_prompt_agent_chat_summarize_ideas,
            run_gpt_prompt_agent_chat_summarize_relationship,
            run_gpt_prompt_agent_chat,
            run_gpt_prompt_summarize_ideas,
            run_gpt_prompt_generate_next_convo_line,
            run_gpt_prompt_generate_whisper_inner_thought,
            run_gpt_prompt_planning_thought_on_convo,
            run_gpt_prompt_memo_on_convo
        )
        print("✅ All 32 functions imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_base_class():
    """Test that the GPTPromptRunner base class is accessible"""
    print("\n" + "=" * 60)
    print("Testing base class...")
    print("=" * 60)

    try:
        from persona.prompt_template.run_gpt_prompt import GPTPromptRunner
        print("✅ GPTPromptRunner base class imported successfully!")

        # Check if it has required methods
        required_methods = ['create_prompt_input', 'func_clean_up', 'func_validate', 'get_fail_safe', 'run']
        for method in required_methods:
            if hasattr(GPTPromptRunner, method):
                print(f"✅ Method '{method}' found")
            else:
                print(f"❌ Method '{method}' missing")
                return False

        return True
    except Exception as e:
        print(f"❌ Base class test failed: {e}")
        return False

def test_runner_classes():
    """Test that all runner classes are defined"""
    print("\n" + "=" * 60)
    print("Testing runner classes...")
    print("=" * 60)

    try:
        from persona.prompt_template.run_gpt_prompt import (
            WakeUpHourRunner,
            DailyPlanRunner,
            GenerateHourlyScheduleRunner,
            TaskDecompRunner
        )
        print("✅ All runner classes imported successfully!")

        # Check that they inherit from GPTPromptRunner
        from persona.prompt_template.run_gpt_prompt import GPTPromptRunner
        for runner_class in [WakeUpHourRunner, DailyPlanRunner, GenerateHourlyScheduleRunner, TaskDecompRunner]:
            if issubclass(runner_class, GPTPromptRunner):
                print(f"✅ {runner_class.__name__} inherits from GPTPromptRunner")
            else:
                print(f"❌ {runner_class.__name__} doesn't inherit from GPTPromptRunner")
                return False

        return True
    except Exception as e:
        print(f"❌ Runner classes test failed: {e}")
        return False

def test_function_signatures():
    """Test that function signatures match expected format"""
    print("\n" + "=" * 60)
    print("Testing function signatures...")
    print("=" * 60)

    import inspect
    from persona.prompt_template.run_gpt_prompt import run_gpt_prompt_wake_up_hour

    # Test signature of one function
    sig = inspect.signature(run_gpt_prompt_wake_up_hour)
    params = list(sig.parameters.keys())

    expected_params = ['persona', 'test_input', 'verbose']
    if params == expected_params:
        print(f"✅ run_gpt_prompt_wake_up_hour has correct signature: {params}")
    else:
        print(f"❌ Signature mismatch. Expected: {expected_params}, Got: {params}")
        return False

    return True

def test_mock_function_calls():
    """Test function calls with mock data (without actual LLM calls)"""
    print("\n" + "=" * 60)
    print("Testing function calls with mock data...")
    print("=" * 60)

    try:
        from persona.prompt_template.run_gpt_prompt import WakeUpHourRunner

        # Create a mock persona object
        class MockScratch:
            def get_str_iss(self):
                return "Mock ISS"
            def get_str_lifestyle(self):
                return "Mock lifestyle"
            def get_str_firstname(self):
                return "MockFirstName"

        class MockPersona:
            def __init__(self):
                self.scratch = MockScratch()

        persona = MockPersona()

        # Test runner initialization
        runner = WakeUpHourRunner(persona)
        print("✅ WakeUpHourRunner initialized successfully")

        # Test create_prompt_input
        prompt_input = runner.create_prompt_input()
        if isinstance(prompt_input, list) and len(prompt_input) == 3:
            print(f"✅ create_prompt_input returns list with {len(prompt_input)} items")
        else:
            print(f"❌ create_prompt_input failed: {prompt_input}")
            return False

        return True
    except Exception as e:
        print(f"❌ Mock function call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Refactored run_gpt_prompt.py")
    print("=" * 60)

    tests = [
        test_imports,
        test_base_class,
        test_runner_classes,
        test_function_signatures,
        test_mock_function_calls
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"\n❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"\n❌ Test {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Refactoring successful!")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
