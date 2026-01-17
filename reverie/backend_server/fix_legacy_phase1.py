#!/usr/bin/env python3
"""
Script to migrate run_gpt_prompt.py from legacy API to modern LLM interface
Phase 1: Replace safe_generate_response with llm_safe_generate_response
Uses regex for more flexible matching
"""

import re

def fix_wake_up_hour_function(content):
    """Fix the wake_up_hour function specifically"""
    # Pattern to match the entire wake_up_hour function's gpt_param and safe_generate_response block
    pattern = r'(  def run_gpt_prompt_wake_up_hour[\s\S]*?)(  gpt_param = \{"engine": "text-davinci-002", "max_tokens": 5,\s+"temperature": 0\.8, "top_p": 1, "stream": False,\s+"frequency_penalty": 0, "presence_penalty": 0, "stop": \["\\n"\]\})([\s\S]*?prompt_template = "persona/prompt_template/v2/wake_up_hour_v1\.txt"[\s\S]*?)(  output = safe_generate_response\(prompt, gpt_param, 5, fail_safe,\s+__func_validate, __func_clean_up\))([\s\S]*?  return output, \[output, prompt, gpt_param, prompt_input, fail_safe\])'

    replacement = r'\1\3  example_output = "8"  # Example: 8 (8am wake up)\n  special_instruction = "Output only a single number representing the hour (e.g., 6, 7, 8)"\n\4\5'

    # First, replace the safe_generate_response call
    content = re.sub(
        r'  output = safe_generate_response\(prompt, gpt_param, 5, fail_safe,\s+__func_validate, __func_clean_up\)',
        '  output = llm_safe_generate_response(prompt, example_output, special_instruction, 5, fail_safe,\n                                     __func_validate, __func_clean_up, model_type="chat")',
        content
    )

    # Then remove the gpt_param block
    content = re.sub(
        r'  gpt_param = \{"engine": "text-davinci-002", "max_tokens": 5,\s+"temperature": 0\.8, "top_p": 1, "stream": False,\s+"frequency_penalty": 0, "presence_penalty": 0, "stop": \["\\n"\]\}\n',
        '',
        content
    )

    # Fix the return statement
    content = re.sub(
        r'  return output, \[output, prompt, gpt_param, prompt_input, fail_safe\]',
        '  return output, [output, prompt, example_output, special_instruction, prompt_input, fail_safe]',
        content
    )

    return content

def fix_daily_plan_function(content):
    """Fix the daily_plan function"""
    # Remove gpt_param block
    content = re.sub(
        r'  gpt_param = \{"engine": "text-davinci-003", "max_tokens": 500,\s+"temperature": 1, "top_p": 1, "stream": False,\s+"frequency_penalty": 0, "presence_penalty": 0, "stop": None\}\n',
        '',
        content
    )

    # Replace safe_generate_response call
    content = re.sub(
        r'  output = safe_generate_response\(prompt, gpt_param, 5, fail_safe,\s+__func_validate, __func_clean_up\)',
        '  output = llm_safe_generate_response(prompt, example_output, special_instruction, 5, fail_safe,\n                                     __func_validate, __func_clean_up, model_type="chat")',
        content
    )

    # Find the location after prompt = generate_prompt(prompt_input, prompt_template)
    # and add example_output and special_instruction
    content = re.sub(
        r'(  prompt = generate_prompt\(prompt_input, prompt_template\))',
        r'\1\n  example_output = "1) wake up and complete the morning routine at 6:00 am, 2) eat breakfast at 7:00 am, 3) work on physics homework from 8:00 am to 11:00 am, 4) have lunch at 12:00 pm, 5) work on research paper from 1:00 pm to 5:00 pm, 6) have dinner at 6:00 pm, 7) watch TV from 7:00 pm to 9:00 pm, 8) go to bed at 10:00 pm"\n  special_instruction = "Output a numbered list of daily activities with times. Each item should start with a number and parentheses like \'1)\'"',
        content
    )

    return content

def main():
    """Apply fixes to run_gpt_prompt.py"""
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    # Apply replacements
    original_length = len(content)

    # Fix specific functions
    content = fix_wake_up_hour_function(content)
    print("✅ Fixed wake_up_hour function")

    content = fix_daily_plan_function(content)
    print("✅ Fixed daily_plan function")

    new_length = len(content)

    print(f"File size changed from {original_length} to {new_length} characters")
    print(f"Size difference: {new_length - original_length} characters")

    with open(file_path, 'w') as f:
        f.write(content)

    print("\nApplied Phase 1 fixes to run_gpt_prompt.py")

if __name__ == "__main__":
    main()
