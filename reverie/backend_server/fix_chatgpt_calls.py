#!/usr/bin/env python3
"""Fix remaining ChatGPT_safe_generate_response calls"""

import re

def main():
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    # Count before
    before_count = len(re.findall(r'ChatGPT_safe_generate_response', content))
    print(f"ChatGPT_safe_generate_response calls before: {before_count}")

    # Replace calls that are NOT in comments
    # Pattern: output = ChatGPT_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
    #                                         __func_validate, __func_clean_up, True)
    content = re.sub(
        r'(\s+)(output = )ChatGPT_safe_generate_response\(prompt, example_output, special_instruction, 3, fail_safe,\n(\s+)(__\w+_validate), (__\w+_clean_up), True\)',
        r'\1\2llm_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,\n\3__func_validate, __func_clean_up, model_type="chat")',
        content
    )

    # Another pattern without True at the end
    content = re.sub(
        r'(\s+)(output = )ChatGPT_safe_generate_response\(prompt, example_output, special_instruction, 3, fail_safe,\n(\s+)(__\w+_validate), (__\w+_clean_up)\)',
        r'\1\2llm_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,\n\3__func_validate, __func_clean_up, model_type="chat")',
        content
    )

    # Count after
    after_count = len(re.findall(r'ChatGPT_safe_generate_response', content))
    print(f"ChatGPT_safe_generate_response calls after: {after_count}")
    print(f"Fixed: {before_count - after_count} calls")

    # Count llm_safe_generate_response
    llm_count = len(re.findall(r'llm_safe_generate_response', content))
    print(f"Total llm_safe_generate_response calls: {llm_count}")

    # Save
    with open(file_path, 'w') as f:
        f.write(content)

    print("✅ File saved")

if __name__ == "__main__":
    main()
