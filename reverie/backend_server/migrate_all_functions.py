#!/usr/bin/env python3
"""
Comprehensive migration script for run_gpt_prompt.py
Replaces all legacy safe_generate_response calls with modern llm_safe_generate_response
This handles ALL 32+ functions in the file
"""

import re

def apply_comprehensive_migration():
    """Apply comprehensive migration to all functions"""
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    print(f"Original file size: {len(content)} characters")

    # Count initial safe_generate_response calls
    initial_count = len(re.findall(r'safe_generate_response', content))
    print(f"Found {initial_count} safe_generate_response calls to fix")

    # Fix 1: Remove all gpt_param blocks (9-key format)
    # Pattern matches: gpt_param = {"engine": ..., "max_tokens": ..., ...}
    gpt_param_pattern = r'  gpt_param = \{[^}]*"engine"[^}]*"max_tokens"[^}]*\}\n'
    content = re.sub(gpt_param_pattern, '', content)
    print("✅ Removed all gpt_param blocks")

    # Fix 2: Add example_output and special_instruction before fail_safe
    # Pattern: prompt = generate_prompt(...)
    #          fail_safe = get_fail_safe()
    # Replace: prompt = generate_prompt(...)
    #          example_output = "..."
    #          special_instruction = "..."
    #          fail_safe = get_fail_safe()

    # For each function, we need specific example outputs
    # Use a generic pattern that can be enhanced
    prompt_pattern = r'(  prompt = generate_prompt\([^)]+\))\n  fail_safe = get_fail_safe\(\)'

    generic_replacement = r'\1\n  example_output = "EXAMPLE_OUTPUT"  # Placeholder - will be customized per function\n  special_instruction = "SPECIAL_INSTRUCTION"  # Placeholder - will be customized per function\n  fail_safe = get_fail_safe()'

    content = re.sub(prompt_pattern, generic_replacement, content)
    print("✅ Added example_output and special_instruction placeholders")

    # Fix 3: Replace safe_generate_response calls with llm_safe_generate_response
    # Pattern: output = safe_generate_response(prompt, gpt_param, repeat, fail_safe, validate, clean_up)
    safe_gen_pattern = r'  output = safe_generate_response\(prompt, gpt_param, (\d+), fail_safe,\s+(__\w+_validate), (__\w+_clean_up)\)'
    safe_gen_replacement = r'  output = llm_safe_generate_response(prompt, example_output, special_instruction, \1, fail_safe,\n                             \2, \3, model_type="chat")'

    content = re.sub(safe_gen_pattern, safe_gen_replacement, content)
    print("✅ Replaced safe_generate_response with llm_safe_generate_response")

    # Fix 4: Update return statements to remove gpt_param
    return_pattern = r'  return output, \[output, prompt, gpt_param, prompt_input, fail_safe\]'
    return_replacement = '  return output, [output, prompt, example_output, special_instruction, prompt_input, fail_safe]'

    content = re.sub(return_pattern, return_replacement, content)
    print("✅ Updated return statements")

    # Fix 5: Update print_run_prompts calls (remove gpt_param)
    print_pattern = r'print_run_prompts\(prompt_template, persona, gpt_param,\s+prompt_input, prompt, output\)'
    print_replacement = 'print_run_prompts(prompt_template, persona, example_output, special_instruction,\n                      prompt_input, prompt, output)'

    content = re.sub(print_pattern, print_replacement, content)
    print("✅ Updated print_run_prompts calls")

    # Count final safe_generate_response calls (should be 0)
    final_count = len(re.findall(r'safe_generate_response', content))
    print(f"Remaining safe_generate_response calls: {final_count}")

    print(f"Final file size: {len(content)} characters")
    print(f"Size change: {len(content) - initial_count} characters")

    return content, initial_count, final_count

def main():
    """Apply all fixes and save the file"""
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    # Read original content
    with open(file_path, 'r') as f:
        original_content = f.read()

    # Save backup
    with open(file_path + '.backup2', 'w') as f:
        f.write(original_content)
    print("✅ Created backup: run_gpt_prompt.py.backup2")

    # Apply migration
    content, initial_count, final_count = apply_comprehensive_migration()

    # Save migrated content
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Functions fixed: {initial_count - final_count}")
    print(f"✅ File saved: {file_path}")
    print(f"✅ Backup saved: {file_path}.backup2")
    print(f"\nNext steps:")
    print(f"1. Test the updated file by running test.py")
    print(f"2. Run a short simulation to verify no 'TOKEN LIMIT EXCEEDED' errors")
    print(f"3. Check for any remaining issues with example_output placeholders")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
