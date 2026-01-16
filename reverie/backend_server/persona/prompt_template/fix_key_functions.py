#!/usr/bin/env python3
"""
Fix the most critical functions in run_gpt_prompt.py
"""

import re

def fix_function(content, func_name, gpt_param_pattern, file_path):
    """Fix a specific function"""
    print(f"Fixing {func_name}...")

    # Remove gpt_param block
    content = re.sub(gpt_param_pattern, '', content)

    # Add example_output and special_instruction
    # Find the line with prompt = generate_prompt(...) and add after it
    pattern = rf'(  prompt = generate_prompt\([^)]+\))\n  fail_safe = get_fail_safe\(\)'

    replacement = r'\1\n  example_output = "EXAMPLE_PLACEHOLDER"\n  special_instruction = "INSTRUCTION_PLACEHOLDER"\n  fail_safe = get_fail_safe()'

    # For now, just do simple replacements to make it work
    return content

def main():
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    print(f"Original size: {len(content)}")

    # Fix 1: Remove all gpt_param blocks (multiple variations)
    # Pattern 1: Standard gpt_param with temperature
    content = re.sub(
        r'  gpt_param = \{"engine": "text-davinci-\d{3}", "max_tokens": \d+,\s+"temperature": [\d\.]+, "top_p": \d+, "stream": False,\s+"frequency_penalty": \d+, "presence_penalty": \d+, "stop": \[.*\]\}\n',
        '',
        content
    )

    # Pattern 2: gpt_param with null stop
    content = re.sub(
        r'  gpt_param = \{"engine": "text-davinci-\d{3}", "max_tokens": \d+,\s+"temperature": [\d\.]+, "top_p": \d+, "stream": False,\s+"frequency_penalty": \d+, "presence_penalty": \d+, "stop": None\}\n',
        '',
        content
    )

    print("✅ Removed gpt_param blocks")

    # Replace all safe_generate_response calls
    content = re.sub(
        r'  output = safe_generate_response\(prompt, gpt_param, (\d+), fail_safe,\s+(__\w+_validate), (__\w+_clean_up)\)',
        r'  output = llm_safe_generate_response(prompt, example_output, special_instruction, \1, fail_safe,\n                             \2, \3, model_type="chat")',
        content
    )

    print("✅ Replaced safe_generate_response calls")

    # Update return statements
    content = re.sub(
        r'  return output, \[output, prompt, gpt_param, prompt_input, fail_safe\]',
        '  return output, [output, prompt, example_output, special_instruction, prompt_input, fail_safe]',
        content
    )

    print("✅ Updated return statements")

    # Add example_output and special_instruction after generate_prompt
    # This is complex - do it for the first few critical functions

    # For run_gpt_prompt_wake_up_hour
    content = re.sub(
        r'(  prompt = generate_prompt\(prompt_input, prompt_template\))',
        r'\1\n  example_output = "8"\n  special_instruction = "Output only a single number representing the hour"',
        content,
        count=1
    )

    # For run_gpt_prompt_daily_plan
    content = re.sub(
        r'(  prompt = generate_prompt\(prompt_input, prompt_template\))',
        r'\1\n  example_output = "1) wake up, 2) eat breakfast, 3) work"\n  special_instruction = "Output numbered list of activities"',
        content,
        count=1
    )

    # For run_gpt_prompt_generate_hourly_schedule
    content = re.sub(
        r'(  prompt = generate_prompt\(prompt_input, prompt_template\))',
        r'\1\n  example_output = "studying for physics exam"\n  special_instruction = "Output activity description only"',
        content,
        count=1
    )

    print("✅ Added example_output and special_instruction")

    print(f"Final size: {len(content)}")

    # Save backup
    with open(file_path + '.backup3', 'w') as f:
        f.write(content)

    # Save main file
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✅ File saved: {file_path}")
    print(f"✅ Backup saved: {file_path}.backup3")

if __name__ == "__main__":
    main()
