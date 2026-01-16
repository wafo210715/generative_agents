"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: run_gpt_prompt.py
Description: Defines all run gpt prompt functions. These functions directly
interface with the safe_generate_response function.
"""
import re
import datetime
import sys
import ast
import random
import string

sys.path.append('../../')

from persona.prompt_template.gpt_structure import (
    generate_prompt,
    llm_safe_generate_response
)
from persona.prompt_template.print_prompt import print_run_prompts


def get_random_alphanumeric(i=6, j=6):
  """
  Returns a random alpha numeric strength that has the length of somewhere
  between i and j.

  INPUT:
    i: min_range for the length
    j: max_range for the length
  OUTPUT:
    an alpha numeric str with the length of somewhere between i and j.
  """
  k = random.randint(i, j)
  x = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
  return x


class GPTPromptRunner:
  """
  Base class for running GPT prompts with standardized interface.

  Each prompt function can be implemented by inheriting from this class
  and overriding the necessary methods.
  """

  def __init__(self, persona, prompt_template, example_output, special_instruction,
               fail_safe_response=None, verbose=False):
    """
    Initialize the prompt runner.

    Args:
      persona: The Persona class instance
      prompt_template: Path to the prompt template file
      example_output: Example output for the LLM
      special_instruction: Special instructions for the LLM
      fail_safe_response: Fail-safe response if LLM fails
      verbose: Whether to print debug output
    """
    self.persona = persona
    self.prompt_template = prompt_template
    self.example_output = example_output
    self.special_instruction = special_instruction
    self.fail_safe_response = fail_safe_response
    self.verbose = verbose

  def create_prompt_input(self, *args, **kwargs):
    """
    Create input for the prompt. To be overridden by subclasses.

    Returns:
      List of inputs for the prompt template
    """
    raise NotImplementedError

  def func_clean_up(self, gpt_response, prompt=""):
    """
    Clean up the GPT response. To be overridden by subclasses.

    Args:
      gpt_response: Raw response from LLM
      prompt: The prompt that was used

    Returns:
      Cleaned up response
    """
    raise NotImplementedError

  def func_validate(self, gpt_response, prompt=""):
    """
    Validate the GPT response. To be overridden by subclasses.

    Args:
      gpt_response: Raw response from LLM
      prompt: The prompt that was used

    Returns:
      Boolean indicating if response is valid
    """
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except:
      return False

  def get_fail_safe(self):
    """
    Get the fail-safe response. Can be overridden by subclasses.

    Returns:
      Fail-safe response
    """
    return self.fail_safe_response

  def run(self, *args, model_type="chat", repeat=5, **kwargs):
    """
    Run the prompt and return the result.

    Args:
      *args: Arguments to pass to create_prompt_input
      model_type: Type of model to use (chat, reasoner, etc.)
      repeat: Number of retry attempts
      **kwargs: Additional arguments

    Returns:
      Tuple of (output, [output, prompt, example_output, special_instruction, prompt_input, fail_safe])
    """
    # Create prompt input
    prompt_input = self.create_prompt_input(*args, **kwargs)

    # Generate prompt
    prompt = generate_prompt(prompt_input, self.prompt_template)

    # Get fail-safe response
    fail_safe = self.get_fail_safe()

    # Call LLM
    output = llm_safe_generate_response(
      prompt,
      self.example_output,
      self.special_instruction,
      model_type=model_type,
      repeat=repeat,
      fail_safe_response=fail_safe,
      func_validate=self.func_validate,
      func_clean_up=self.func_clean_up
    )

    # Print debug info if requested
    if self.verbose:
      print_run_prompts(self.prompt_template, self.persona, self.example_output,
                       self.special_instruction, prompt_input, prompt, output)

    # Return output and metadata
    return output, [output, prompt, self.example_output, self.special_instruction,
                   prompt_input, fail_safe]


##############################################################################
# CHAPTER 1: Run GPT Prompt
##############################################################################

# Wake up hour prompt
class WakeUpHourRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/wake_up_hour_v1.txt",
      example_output="8",
      special_instruction="Output only a single number representing the hour",
      fail_safe_response=8,
      verbose=False
    )

  def create_prompt_input(self, test_input=None):
    if test_input:
      return test_input
    return [
      self.persona.scratch.get_str_iss(),
      self.persona.scratch.get_str_lifestyle(),
      self.persona.scratch.get_str_firstname()
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return int(gpt_response.strip().lower().split("am")[0])


def run_gpt_prompt_wake_up_hour(persona, test_input=None, verbose=False):
  """
  Given the persona, returns an integer that indicates the hour when the
  persona wakes up.

  INPUT:
    persona: The Persona class instance
  OUTPUT:
    integer for the wake up hour.
  """
  runner = WakeUpHourRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(test_input=test_input)


# Daily plan prompt
class DailyPlanRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/daily_planning_v1.txt",
      example_output=[
        "wake up and complete the morning routine at 6:00 am",
        "eat breakfast at 7:00 am"
      ],
      special_instruction="Output numbered list of activities",
      fail_safe_response=[
        'wake up and complete the morning routine at 6:00 am',
        'eat breakfast at 7:00 am',
        'read a book from 8:00 am to 12:00 pm',
        'have lunch at 12:00 pm',
        'take a nap from 1:00 pm to 4:00 pm',
        'relax and watch TV from 7:00 pm to 8:00 pm',
        'go to bed at 11:00 pm'
      ],
      verbose=False
    )

  def create_prompt_input(self, wake_up_hour, test_input=None):
    if test_input:
      return test_input
    return [
      self.persona.scratch.get_str_iss(),
      self.persona.scratch.get_str_lifestyle(),
      self.persona.scratch.get_str_curr_date_str(),
      self.persona.scratch.get_str_firstname(),
      f"{str(wake_up_hour)}:00 am"
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    result = []
    parts = gpt_response.split(")")
    for part in parts:
      if part and part[-1].isdigit():
        part = part[:-1].strip()
        if part and part[-1] in [".", ","]:
          part = part[:-1].strip()
        if part:
          result.append(part)
    return result


def run_gpt_prompt_daily_plan(persona, wake_up_hour, test_input=None, verbose=False):
  """
  Generates a full day's schedule of broad activities. Returns a list
  of high-level actions for the day.

  INPUT:
    persona: The Persona class instance
    wake_up_hour: The hour the persona wakes up
  OUTPUT:
    a list of daily actions in broad strokes.
  """
  runner = DailyPlanRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(wake_up_hour, test_input=test_input)
