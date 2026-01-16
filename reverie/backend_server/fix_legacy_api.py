#!/usr/bin/env python3
"""
Script to migrate run_gpt_prompt.py from legacy API to modern LLM interface
Phase 1: Replace safe_generate_response with llm_safe_generate_response
"""

def replace_safe_generate_response(content):
    """
    Replace all safe_generate_response calls with llm_safe_generate_response
    This is a comprehensive replacement that handles the pattern variations
    """

    # Pattern for wake_up_hour function
    content = content.replace(
        '''  gpt_param = {"engine": "text-davinci-002", "max_tokens": 5,
             "temperature": 0.8, "top_p": 1, "stream": False,
             "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\\n"]}
  prompt_template = "persona/prompt_template/v2/wake_up_hour_v1.txt"
  prompt_input = create_prompt_input(persona, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()

  output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
                                   __func_validate, __func_clean_up)''',
        '''  prompt_template = "persona/prompt_template/v2/wake_up_hour_v1.txt"
  prompt_input = create_prompt_input(persona, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  example_output = "8"  # Example: 8 (8am wake up)
  special_instruction = "Output only a single number representing the hour (e.g., 6, 7, 8)"
  fail_safe = get_fail_safe()

  output = llm_safe_generate_response(prompt, example_output, special_instruction, 5, fail_safe,
                                     __func_validate, __func_clean_up, model_type="chat")'''
    )

    # Pattern for daily_plan function - first fix the content block
    content = content.replace(
        '''  gpt_param = {"engine": "text-davinci-003", "max_tokens": 500,
               "temperature": 1, "top_p": 1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/daily_planning_v1.txt"
  prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()

  output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
                                   __func_validate, __func_clean_up)''',
        '''  prompt_template = "persona/prompt_template/v2/daily_planning_v1.txt"
  prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  example_output = "1) wake up and complete the morning routine at 6:00 am, 2) eat breakfast at 7:00 am, 3) work on physics homework from 8:00 am to 11:00 am, 4) have lunch at 12:00 pm, 5) work on research paper from 1:00 pm to 5:00 pm, 6) have dinner at 6:00 pm, 7) watch TV from 7:00 pm to 9:00 pm, 8) go to bed at 10:00 pm"
  special_instruction = "Output a numbered list of daily activities with times. Each item should start with a number and parentheses like '1)'"
  fail_safe = get_fail_safe()

  output = llm_safe_generate_response(prompt, example_output, special_instruction, 5, fail_safe,
                                     __func_validate, __func_clean_up, model_type="chat")'''
    )

    # Fix return statements to remove gpt_param
    content = content.replace(
        '  return output, [output, prompt, gpt_param, prompt_input, fail_safe]',
        '  return output, [output, prompt, example_output, special_instruction, prompt_input, fail_safe]'
    )

    return content

def main():
    """Apply fixes to run_gpt_prompt.py"""
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    # Apply replacements
    original_length = len(content)
    content = replace_safe_generate_response(content)
    new_length = len(content)

    print(f"File size changed from {original_length} to {new_length} characters")
    print(f"Size difference: {new_length - original_length} characters")

    with open(file_path, 'w') as f:
        f.write(content)

    print("Applied Phase 1 fixes to run_gpt_prompt.py")

if __name__ == "__main__":
    main()
