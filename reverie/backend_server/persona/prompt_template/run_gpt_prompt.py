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


###############################################################################
# Chapter 1: Run GPT Prompt
###############################################################################

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
      prompt_template="persona/prompt_template/v2/daily_planning_v6.txt",
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


# Generate hourly schedule prompt
class GenerateHourlyScheduleRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_hourly_schedule_v2.txt",
      example_output="studying for her music classes",
      special_instruction="Output ONLY the activity description without the persona name",
      fail_safe_response="asleep",
      verbose=False
    )

  def create_prompt_input(self, curr_hour_str, p_f_ds_hourly_org, hour_str, intermission2=None, test_input=None):
    if test_input:
      return test_input

    schedule_format = ""
    for i in hour_str:
      schedule_format += f"[{self.persona.scratch.get_str_curr_date_str()} -- {i}]"
      schedule_format += f" Activity: [Fill in]\n"
    schedule_format = schedule_format[:-1]

    intermission_str = f"Here the originally intended hourly breakdown of"
    intermission_str += f" {self.persona.scratch.get_str_firstname()}'s schedule today: "
    for count, i in enumerate(self.persona.scratch.daily_req):
      intermission_str += f"{str(count+1)}) {i}, "
    intermission_str = intermission_str[:-2]

    prior_schedule = ""
    if p_f_ds_hourly_org:
      prior_schedule = "\n"
      for count, i in enumerate(p_f_ds_hourly_org):
        prior_schedule += f"[(ID:{get_random_alphanumeric()})"
        prior_schedule += f" {self.persona.scratch.get_str_curr_date_str()} --"
        prior_schedule += f" {hour_str[count]}] Activity:"
        prior_schedule += f" {self.persona.scratch.get_str_firstname()}"
        prior_schedule += f" is {i}\n"

    prompt_ending = f"[(ID:{get_random_alphanumeric()})"
    prompt_ending += f" {self.persona.scratch.get_str_curr_date_str()}"
    prompt_ending += f" -- {curr_hour_str}] Activity:"
    prompt_ending += f" {self.persona.scratch.get_str_firstname()} is"

    if intermission2:
      intermission2 = f"\n{intermission2}"

    return [
      schedule_format,
      self.persona.scratch.get_str_iss(),
      prior_schedule + "\n",
      intermission_str,
      intermission2 if intermission2 else "",
      prompt_ending
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    response = gpt_response.strip()
    if response and response[-1] == ".":
      response = response[:-1]
    return response


def run_gpt_prompt_generate_hourly_schedule(persona, curr_hour_str, p_f_ds_hourly_org, hour_str, intermission2=None, test_input=None, verbose=False):
  """
  Generates hourly schedule entries for the persona.

  INPUT:
    persona: The Persona class instance
    curr_hour_str: Current hour string
    p_f_ds_hourly_org: Prior hourly schedule
    hour_str: Hour strings list
    intermission2: Additional intermission text
  OUTPUT:
    The generated activity for the current hour.
  """
  runner = GenerateHourlyScheduleRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(curr_hour_str, p_f_ds_hourly_org, hour_str, intermission2, test_input=test_input)


# Task decomposition prompt
class TaskDecompRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/task_decomp_v3.txt",
      example_output="[['waking up and completing her morning routine', 60]]",
      special_instruction="Output ONLY a JSON list of lists, no extra text. Format: [['Task Name', duration_in_minutes], ...]",
      fail_safe_response=[['waiting', 5]],
      verbose=False
    )

  def create_prompt_input(self, task, duration, test_input=None):
    if test_input:
      return test_input

    curr_f_org_index = self.persona.scratch.get_f_daily_schedule_hourly_org_index()
    all_indices = []
    all_indices += [curr_f_org_index]
    if curr_f_org_index+1 <= len(self.persona.scratch.f_daily_schedule_hourly_org):
      all_indices += [curr_f_org_index+1]
    if curr_f_org_index+2 <= len(self.persona.scratch.f_daily_schedule_hourly_org):
      all_indices += [curr_f_org_index+2]

    curr_time_range = ""
    summ_str = f'Today is {self.persona.scratch.curr_time.strftime("%B %d, %Y")}. '
    summ_str += f'From '
    for index in all_indices:
      if index < len(self.persona.scratch.f_daily_schedule_hourly_org):
        start_min = 0
        for i in range(index):
          start_min += self.persona.scratch.f_daily_schedule_hourly_org[i][1]
        end_min = start_min + self.persona.scratch.f_daily_schedule_hourly_org[index][1]
        start_time = (datetime.datetime.strptime("00:00:00", "%H:%M:%S")
                      + datetime.timedelta(minutes=start_min))
        end_time = (datetime.datetime.strptime("00:00:00", "%H:%M:%S")
                    + datetime.timedelta(minutes=end_min))
        start_time_str = start_time.strftime("%H:%M%p")
        end_time_str = end_time.strftime("%H:%M%p")
        summ_str += f"{start_time_str} ~ {end_time_str}, {self.persona.name} is planning on {self.persona.scratch.f_daily_schedule_hourly_org[index][0]}, "
        if curr_f_org_index+1 == index:
          curr_time_range = f'{start_time_str} ~ {end_time_str}'
    summ_str = summ_str[:-2] + "."

    return [
      self.persona.scratch.get_str_iss(),
      summ_str,
      self.persona.scratch.get_str_firstname(),
      self.persona.scratch.get_str_firstname(),
      task,
      curr_time_range,
      duration,
      self.persona.scratch.get_str_firstname()
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    import json

    # Handle escaped newlines
    cleaned_response = gpt_response.replace('\\n', '\n').strip()

    # Try parsing the response
    try:
      # If it's already a valid JSON-like format, parse it
      if cleaned_response.startswith('[') and cleaned_response.endswith(']'):
        parsed = ast.literal_eval(cleaned_response)
        return parsed
    except:
      pass

    # Fallback to original parsing logic
    temp_lines = [i.strip() for i in cleaned_response.split("\n") if i.strip()]
    if not temp_lines:
      return [["waiting", 5]]

    tasks = []
    for line in temp_lines:
      try:
        # Extract task and duration
        if "(duration in minutes:" in line:
          parts = line.split("(duration in minutes:")
          task_name = parts[0].strip()
          if task_name.endswith('.'):
            task_name = task_name[:-1]

          # Extract duration
          duration_part = parts[1].split(",")[0].strip() if len(parts) > 1 else "5"
          duration_part = duration_part.rstrip(')').strip()
          try:
            duration = max(1, int(duration_part))
          except ValueError:
            duration = 5

          tasks.append([task_name, duration])
      except:
        continue

    if not tasks:
      return [["waiting", 5]]

    # Extract total expected minutes from prompt
    try:
      total_expected_min_str = prompt.split("(total duration in minutes")[-1]
      total_expected_min = int(total_expected_min_str.split(":")[0].strip())
    except (ValueError, IndexError):
      total_expected_min = sum(task[1] for task in tasks)

    # Create minute-by-minute task list and consolidate
    current_minute_slots = []
    for i, (task_name, duration) in enumerate(tasks):
      duration_rounded = duration - (duration % 5)
      if duration_rounded > 0:
        current_minute_slots.extend([(task_name, i)] * duration_rounded)

    # Adjust to match total expected minutes
    if len(current_minute_slots) > total_expected_min:
      cutoff_index = min(60, len(current_minute_slots) - 1)
      last_task = current_minute_slots[cutoff_index]
      for i in range(1, min(6, len(current_minute_slots))):
        if len(current_minute_slots) - i >= 0:
          current_minute_slots[-i] = last_task
    elif len(current_minute_slots) < total_expected_min:
      if current_minute_slots:
        last_task = current_minute_slots[-1]
        padding_needed = total_expected_min - len(current_minute_slots)
        current_minute_slots.extend([last_task] * padding_needed)

    # Consolidate consecutive same tasks
    consolidated = []
    for task_name, task_index in current_minute_slots:
      if not consolidated or task_name != consolidated[-1][0]:
        consolidated.append([task_name, 1])
      else:
        consolidated[-1][1] += 1

    return consolidated

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return isinstance(result, list) and len(result) > 0
    except:
      return False


def run_gpt_prompt_task_decomp(persona, task, duration, test_input=None, verbose=False):
  """
  Breaks down complex activities into timed subtasks.

  INPUT:
    persona: The Persona class instance
    task: The task to decompose
    duration: Duration in minutes
  OUTPUT:
    List of [task_name, duration] pairs.
  """
  runner = TaskDecompRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(task, duration, test_input=test_input)


# Action sector prompt
class ActionSectorRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v1/action_location_sector_v1.txt",
      example_output="Johnson Park",
      special_instruction="The value for the output must contain one of the area options above verbatim (including lower/upper case).",
      fail_safe_response=None,
      verbose=False
    )

  def create_prompt_input(self, action_description, maze, test_input=None):
    if test_input:
      return test_input

    act_world = f"{maze.access_tile(self.persona.scratch.curr_tile)['world']}"

    prompt_input = []

    prompt_input += [self.persona.scratch.get_str_name()]
    prompt_input += [self.persona.scratch.living_area.split(":")[1]]
    x = f"{act_world}:{self.persona.scratch.living_area.split(':')[1]}"
    prompt_input += [self.persona.s_mem.get_str_accessible_sector_arenas(x)]

    prompt_input += [self.persona.scratch.get_str_name()]
    prompt_input += [f"{maze.access_tile(self.persona.scratch.curr_tile)['sector']}"]
    x = f"{act_world}:{maze.access_tile(self.persona.scratch.curr_tile)['sector']}"
    prompt_input += [self.persona.s_mem.get_str_accessible_sector_arenas(x)]

    if self.persona.scratch.get_str_daily_plan_req() != "":
      prompt_input += [f"\n{self.persona.scratch.get_str_daily_plan_req()}"]
    else:
      prompt_input += [""]

    # MAR 11 TEMP
    accessible_sector_str = self.persona.s_mem.get_str_accessible_sectors(act_world)
    curr = accessible_sector_str.split(", ")
    fin_accessible_sectors = []
    for i in curr:
      if "'s house" in i:
        if self.persona.scratch.last_name in i:
          fin_accessible_sectors += [i]
      else:
        fin_accessible_sectors += [i]
    accessible_sector_str = ", ".join(fin_accessible_sectors)
    # END MAR 11 TEMP

    prompt_input += [accessible_sector_str]

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description:
      action_description_1 = action_description.split("(")[0].strip()
      action_description_2 = action_description.split("(")[-1][:-1]
    prompt_input += [self.persona.scratch.get_str_name()]
    prompt_input += [action_description_1]

    prompt_input += [action_description_2]
    prompt_input += [self.persona.scratch.get_str_name()]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    cleaned_response = gpt_response.split("}")[0]
    return cleaned_response

  def func_validate(self, gpt_response, prompt=""):
    if len(gpt_response.strip()) < 1:
      return False
    if "}" not in gpt_response:
      return False
    if "," in gpt_response:
      return False
    return True

  def get_fail_safe(self):
    # Get accessible sectors for validation
    act_world = f"{self.persona.scratch.curr_tile[2]}"  # Assuming curr_tile has world info
    accessible_sectors = self.persona.s_mem.get_str_accessible_sectors(act_world)
    if accessible_sectors:
      sectors = [s.strip() for s in accessible_sectors.split(",")]
      return random.choice(sectors)
    return "kitchen"

  def run(self, action_description, maze, *args, **kwargs):
    output, metadata = super().run(action_description, maze, *args, **kwargs)

    # Validate output is in accessible sectors
    act_world = f"{maze.access_tile(self.persona.scratch.curr_tile)['world']}"
    x = [i.strip() for i in self.persona.s_mem.get_str_accessible_sectors(act_world).split(",")]
    if output not in x:
      output = self.persona.scratch.living_area.split(":")[1]

    print("DEBUG", random.choice(x), "------", output)

    return output, metadata


def run_gpt_prompt_action_sector(action_description, persona, maze, test_input=None, verbose=False):
  """
  Determines the sector for a given action description.

  INPUT:
    action_description: The action description
    persona: The Persona class instance
    maze: The Maze instance
  OUTPUT:
    The selected sector name.
  """
  runner = ActionSectorRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(action_description, maze, test_input=test_input)


# Action arena prompt
class ActionArenaRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v1/action_location_object_vMar11.txt",
      example_output="kitchen",
      special_instruction="The output must be exactly one of the area options above (case sensitive).",
      fail_safe_response=None,
      verbose=False
    )

  def create_prompt_input(self, action_description, maze, act_world, act_sector, test_input=None):
    if test_input:
      return test_input

    prompt_input = []
    prompt_input += [self.persona.scratch.get_str_name()]
    x = f"{act_world}:{act_sector}"
    prompt_input += [act_sector]

    # MAR 11 TEMP
    accessible_arena_str = self.persona.s_mem.get_str_accessible_sector_arenas(x)
    curr = accessible_arena_str.split(", ")
    fin_accessible_arenas = []
    for i in curr:
      if "'s room" in i:
        if self.persona.scratch.last_name in i:
          fin_accessible_arenas += [i]
      else:
        fin_accessible_arenas += [i]
    accessible_arena_str = ", ".join(fin_accessible_arenas)
    # END MAR 11 TEMP

    prompt_input += [accessible_arena_str]

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description:
      action_description_1 = action_description.split("(")[0].strip()
      action_description_2 = action_description.split("(")[-1][:-1]
    prompt_input += [self.persona.scratch.get_str_name()]
    prompt_input += [action_description_1]

    prompt_input += [action_description_2]
    prompt_input += [self.persona.scratch.get_str_name()]

    prompt_input += [act_sector]

    prompt_input += [accessible_arena_str]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    cleaned_response = gpt_response.split("}")[0]
    return cleaned_response

  def func_validate(self, gpt_response, prompt=""):
    if len(gpt_response.strip()) < 1:
      return False
    if "}" not in gpt_response:
      return False
    if "," in gpt_response:
      return False
    return True

  def get_fail_safe(self):
    return "kitchen"


def run_gpt_prompt_action_arena(action_description, persona, maze, act_world, act_sector, test_input=None, verbose=False):
  """
  Determines the arena for a given action description.

  INPUT:
    action_description: The action description
    persona: The Persona class instance
    maze: The Maze instance
    act_world: The world name
    act_sector: The sector name
  OUTPUT:
    The selected arena name.
  """
  runner = ActionArenaRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(action_description, maze, act_world, act_sector, test_input=test_input)


# Action game object prompt
class ActionGameObjectRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v1/action_object_v2.txt",
      example_output="bed",
      special_instruction="Output ONLY the selected game object name, no extra text.",
      fail_safe_response=None,
      verbose=False
    )

  def create_prompt_input(self, action_description, temp_address, test_input=None):
    if test_input:
      return test_input

    prompt_input = []
    if "(" in action_description:
      action_description = action_description.split("(")[-1][:-1]

    prompt_input += [action_description]
    prompt_input += [self.persona.s_mem.get_str_accessible_arena_game_objects(temp_address)]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1

  def get_fail_safe(self):
    return "bed"

  def run(self, action_description, temp_address, *args, **kwargs):
    output, metadata = super().run(action_description, temp_address, *args, **kwargs)

    # Validate output is in accessible game objects
    x = [i.strip() for i in self.persona.s_mem.get_str_accessible_arena_game_objects(temp_address).split(",")]
    if output not in x:
      output = random.choice(x)

    return output, metadata


def run_gpt_prompt_action_game_object(action_description, persona, maze, temp_address, test_input=None, verbose=False):
  """
  Determines the game object for a given action description.

  INPUT:
    action_description: The action description
    persona: The Persona class instance
    maze: The Maze instance
    temp_address: The temporary address (world:sector:arena)
  OUTPUT:
    The selected game object name.
  """
  runner = ActionGameObjectRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(action_description, temp_address, test_input=test_input)


# Pronunciatio prompt
class PronunciatioRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_pronunciatio_v1.txt",
      example_output="🎶",
      special_instruction="Output ONLY a single emoji, no text.",
      fail_safe_response="💡",
      verbose=False
    )

  def create_prompt_input(self, action_description, test_input=None):
    if test_input:
      return test_input

    if "(" in action_description:
      action_description = action_description.split("(")[-1].split(")")[0]

    return [action_description]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1


def run_gpt_prompt_pronunciatio(action_description, persona, test_input=None, verbose=False):
  """
  Generates an emoji representation (pronunciatio) for an action.

  INPUT:
    action_description: The action description
    persona: The Persona class instance
  OUTPUT:
    A single emoji character.
  """
  runner = PronunciatioRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(action_description, test_input=test_input)


# Event triple prompt
class EventTripleRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_event_triple_v1.txt",
      example_output="['Isabella Rodriguez', 'waiting', 'the cafe']",
      special_instruction="Output ONLY a Python list format with 3 elements: ['subject', 'predicate', 'object']",
      fail_safe_response="['person', 'is', 'idle']",
      verbose=False
    )

  def create_prompt_input(self, action_description, test_input=None):
    if test_input:
      return test_input

    return [action_description]

  def func_clean_up(self, gpt_response, prompt=""):
    cr = gpt_response.strip()
    if cr[-1] == ".":
      cr = cr[:-2]
    return cr

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return "['" in result and "', '" in result
    except:
      return False


def run_gpt_prompt_event_triple(action_description, persona, test_input=None, verbose=False):
  """
  Generates an event triple (subject-predicate-object) for an action.

  INPUT:
    action_description: The action description
    persona: The Persona class instance
  OUTPUT:
    A list of [subject, predicate, object].
  """
  runner = EventTripleRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(action_description, test_input=test_input)


# Act object description prompt
class ActObjDescRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_obj_event_v1.txt",
      example_output="she was on her way to do grocery shopping for lunch",
      special_instruction="Output ONLY the action description, no formatting.",
      fail_safe_response="an idle action",
      verbose=False
    )

  def create_prompt_input(self, act_game_object, act_desp, test_input=None):
    if test_input:
      return test_input

    return [act_game_object, self.persona.scratch.get_str_name(), act_desp]

  def func_clean_up(self, gpt_response, prompt=""):
    cr = gpt_response.strip()
    if cr[-1] == ".":
      cr = cr[:-2]
    return cr

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1


def run_gpt_prompt_act_obj_desc(act_game_object, act_desp, persona, test_input=None, verbose=False):
  """
  Generates a description for an action involving a game object.

  INPUT:
    act_game_object: The game object involved in the action
    act_desp: Original action description
    persona: The Persona class instance
  OUTPUT:
    A description of the action.
  """
  runner = ActObjDescRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(act_game_object, act_desp, test_input=test_input)


# Act object event triple prompt
class ActObjEventTripleRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_event_triple_v1.txt",
      example_output="['Isabella Rodriguez', 'waiting', 'the cafe']",
      special_instruction="Output ONLY a Python list format with 3 elements: ['subject', 'predicate', 'object']",
      fail_safe_response="['person', 'is', 'idle']",
      verbose=False
    )

  def create_prompt_input(self, act_game_object, act_obj_desc, test_input=None):
    if test_input:
      return test_input

    return [f"{self.persona.scratch.get_str_name()} is {act_obj_desc} {act_game_object}"]

  def func_clean_up(self, gpt_response, prompt=""):
    cr = gpt_response.strip()
    if cr[-1] == ".":
      cr = cr[:-2]
    return cr

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return "['" in result and "', '" in result
    except:
      return False


def run_gpt_prompt_act_obj_event_triple(act_game_object, act_obj_desc, persona, test_input=None, verbose=False):
  """
  Generates an event triple for an action involving a game object.

  INPUT:
    act_game_object: The game object involved in the action
    act_obj_desc: Description of the action with object
    persona: The Persona class instance
  OUTPUT:
    A list of [subject, predicate, object].
  """
  runner = ActObjEventTripleRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(act_game_object, act_obj_desc, test_input=test_input)


# Create conversation prompt
class CreateConversationRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/create_conversation_v2.txt",
      example_output='["Hello!", "Hi there!", "How are you?"]',
      special_instruction="Output ONLY a JSON array of strings, no extra text. Example: ['line1', 'line2', 'line3']",
      fail_safe_response=["Hi"],
      verbose=False
    )

  def create_prompt_input(self, target_persona, curr_loc, retrieved, test_input=None):
    if test_input:
      return test_input

    prev_convo_insert = ""
    if self.persona.a_mem.get_last_chat(target_persona.name):
      prev_convo_insert = "[The previous conversation]"

    init_iss = f"I'm {self.persona.scratch.get_str_iss()}"
    prompt_input = [init_iss, prev_convo_insert,
                   self.persona.scratch.get_str_curr_date_str(),
                   curr_loc, self.persona.scratch.get_str_firstname(),
                   target_persona.scratch.get_str_firstname(),
                   retrieved]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    return ast.literal_eval(gpt_response)

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return isinstance(result, list) and len(result) > 0
    except:
      return False


def run_gpt_prompt_create_conversation(persona, target_persona, curr_loc, retrieved, test_input=None, verbose=False):
  """
  Creates a conversation between two personas.

  INPUT:
    persona: The initiating persona
    target_persona: The target persona
    curr_loc: Current location
    retrieved: Retrieved memories
  OUTPUT:
    A list of conversation lines.
  """
  runner = CreateConversationRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, curr_loc, retrieved, test_input=test_input)


# Decide to talk prompt
class DecideToTalkRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/decide_to_talk_v2.txt",
      example_output="Answer in yes or no: yes",
      special_instruction="Output must start with 'Answer in yes or no: ' followed by yes or no.",
      fail_safe_response="yes",
      verbose=False
    )

  def create_prompt_input(self, target_persona, retrieved, test_input=None):
    if test_input:
      return test_input

    last_chat = self.persona.a_mem.get_last_chat(target_persona.name)
    last_chatted_time = ""
    last_chat_about = ""
    if last_chat:
      last_chatted_time = last_chat.created.strftime("%B %d, %Y, %H:%M:%S")
      last_chat_about = last_chat.description

    context = ""
    for c_node in retrieved["events"]:
      curr_desc = c_node.description.split(" ")
      curr_desc[2:3] = ["was"]
      curr_desc = " ".join(curr_desc)
      context += f"{curr_desc}. "
    context += "\n"
    for c_node in retrieved["thoughts"]:
      context += f"{c_node.description}. "

    curr_time = self.persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
    init_act_desc = self.persona.scratch.act_description
    if "(" in init_act_desc:
      init_act_desc = init_act_desc.split("(")[-1][:-1]

    if len(self.persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
      init_p_desc = f"{self.persona.name} is already {init_act_desc}"
    elif "waiting" in init_act_desc:
      init_p_desc = f"{self.persona.name} is {init_act_desc}"
    else:
      init_p_desc = f"{self.persona.name} is on the way to {init_act_desc}"

    target_act_desc = target_persona.scratch.act_description
    if "(" in target_act_desc:
      target_act_desc = target_act_desc.split("(")[-1][:-1]

    if len(target_persona.scratch.planned_path) == 0 and "waiting" not in target_act_desc:
      target_p_desc = f"{target_persona.name} is already {target_act_desc}"
    elif "waiting" in target_act_desc:
      target_p_desc = f"{target_persona.name} is {target_act_desc}"
    else:
      target_p_desc = f"{target_persona.name} is on the way to {target_act_desc}"

    prompt_input = []
    prompt_input += [context]
    prompt_input += [curr_time]
    prompt_input += [self.persona.name]
    prompt_input += [target_persona.name]
    prompt_input += [last_chatted_time]
    prompt_input += [last_chat_about]
    prompt_input += [init_p_desc]
    prompt_input += [target_p_desc]
    prompt_input += [self.persona.name]
    prompt_input += [target_persona.name]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split("Answer in yes or no:")[-1].strip().lower()

  def func_validate(self, gpt_response, prompt=""):
    try:
      return gpt_response.split("Answer in yes or no:")[-1].strip().lower() in ["yes", "no"]
    except:
      return False

  def get_fail_safe(self):
    return "yes"


def run_gpt_prompt_decide_to_talk(persona, target_persona, retrieved, test_input=None, verbose=False):
  """
  Determines whether persona should talk to target_persona.

  INPUT:
    persona: The initiating persona
    target_persona: The target persona
    retrieved: Retrieved memories
  OUTPUT:
    "yes" or "no".
  """
  runner = DecideToTalkRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, retrieved, test_input=test_input)


# Decide to react prompt
class DecideToReactRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/decide_to_react_v2.txt",
      example_output="Answer in yes, no, or wait: yes",
      special_instruction="Output must start with 'Answer in yes, no, or wait: ' followed by yes, no, or wait.",
      fail_safe_response="no",
      verbose=False
    )

  def create_prompt_input(self, target_persona, retrieved, test_input=None):
    if test_input:
      return test_input

    context = ""
    for c_node in retrieved["events"]:
      curr_desc = c_node.description.split(" ")
      curr_desc[2:3] = ["was"]
      curr_desc = " ".join(curr_desc)
      context += f"{curr_desc}. "
    context += "\n"
    for c_node in retrieved["thoughts"]:
      context += f"{c_node.description}. "

    curr_time = self.persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
    init_act_desc = self.persona.scratch.act_description
    if "(" in init_act_desc:
      init_act_desc = init_act_desc.split("(")[-1][:-1]

    if len(self.persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
      init_p_desc = f"{self.persona.name} is already {init_act_desc}"
    elif "waiting" in init_act_desc:
      init_p_desc = f"{self.persona.name} is {init_act_desc}"
    else:
      init_p_desc = f"{self.persona.name} is on the way to {init_act_desc}"

    target_act_desc = target_persona.scratch.act_description
    if "(" in target_act_desc:
      target_act_desc = target_act_desc.split("(")[-1][:-1]

    prompt_input = []
    prompt_input += [context]
    prompt_input += [curr_time]
    prompt_input += [self.persona.name]
    prompt_input += [target_persona.name]
    prompt_input += [init_p_desc]
    prompt_input += [target_act_desc]
    prompt_input += [self.persona.name]
    prompt_input += [target_persona.name]
    return prompt_input

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split("Answer in yes, no, or wait:")[-1].strip().lower()

  def func_validate(self, gpt_response, prompt=""):
    try:
      return gpt_response.split("Answer in yes, no, or wait:")[-1].strip().lower() in ["yes", "no", "wait"]
    except:
      return False

  def get_fail_safe(self):
    return "no"


def run_gpt_prompt_decide_to_react(persona, target_persona, retrieved, test_input=None, verbose=False):
  """
  Determines whether persona should react to target_persona.

  INPUT:
    persona: The reacting persona
    target_persona: The target persona
    retrieved: Retrieved memories
  OUTPUT:
    "yes", "no", or "wait".
  """
  runner = DecideToReactRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, retrieved, test_input=test_input)


# Summarize conversation prompt
class SummarizeConversationRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/summarize_conversation_v1.txt",
      example_output="isabella and klaus were conversing about klaus's gcset and generator...",
      special_instruction="Output ONLY a single paragraph summary, no formatting.",
      fail_safe_response="a conversation",
      verbose=False
    )

  def create_prompt_input(self, conversation, test_input=None):
    if test_input:
      return test_input

    convo_str = ""
    for row in conversation:
      convo_str += f"{row[0]}: {row[1]}\n"
    return [convo_str]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.strip()

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1


def run_gpt_prompt_summarize_conversation(persona, conversation, test_input=None, verbose=False):
  """
  Summarizes a conversation.

  INPUT:
    persona: The Persona class instance
    conversation: List of [speaker, utterance] pairs
  OUTPUT:
    A summary of the conversation.
  """
  runner = SummarizeConversationRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(conversation, test_input=test_input)


# Extract keywords prompt
class ExtractKeywordsRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/get_keywords_v1.txt",
      example_output="[cleaning, halmos College, restaurant, lunch]",
      special_instruction="Output ONLY a Python list of keywords in brackets, no extra text.",
      fail_safe_response=["life"],
      verbose=False
    )

  def create_prompt_input(self, description, test_input=None):
    if test_input:
      return test_input

    return [description]

  def func_clean_up(self, gpt_response, prompt=""):
    return ast.literal_eval(gpt_response)

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return isinstance(result, list) and len(result) > 0
    except:
      return False


def run_gpt_prompt_extract_keywords(persona, description, test_input=None, verbose=False):
  """
  Extracts keywords from a description.

  INPUT:
    persona: The Persona class instance
    description: The text to extract keywords from
  OUTPUT:
    A list of keywords.
  """
  runner = ExtractKeywordsRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(description, test_input=test_input)


# Keyword to thoughts prompt
class KeywordToThoughtsRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/keyword_to_thoughts_v1.txt",
      example_output="musings on lunch and the \\\"special moment\\\" over lunch",
      special_instruction="Output ONLY the thought string, no formatting or quotes.",
      fail_safe_response="thinking about lunch",
      verbose=False
    )

  def create_prompt_input(self, keyword, concept_summary, test_input=None):
    if test_input:
      return test_input

    return [f"{keyword}: {concept_summary}"]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.strip()

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1


def run_gpt_prompt_keyword_to_thoughts(persona, keyword, concept_summary, test_input=None, verbose=False):
  """
  Generates thoughts based on a keyword and concept summary.

  INPUT:
    persona: The Persona class instance
    keyword: The keyword to focus on
    concept_summary: Summary of the concept
  OUTPUT:
    A thought string.
  """
  runner = KeywordToThoughtsRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(keyword, concept_summary, test_input=test_input)


# Event poignancy prompt
class EventPoignancyRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/poignancy_event_v1.txt",
      example_output="5",
      special_instruction="Output ONLY a single integer between 1-10.",
      fail_safe_response=5,
      verbose=False
    )

  def create_prompt_input(self, event_description, test_input=None):
    if test_input:
      return test_input

    return [
      self.persona.scratch.get_str_name(),
      self.persona.scratch.get_str_iss(),
      self.persona.scratch.get_str_iss(),
      event_description
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return int(gpt_response.strip())

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = int(gpt_response.strip())
      return 1 <= result <= 10
    except:
      return False


def run_gpt_prompt_event_poignancy(persona, event_description, test_input=None, verbose=False):
  """
  Estimates the poignancy of an event.

  INPUT:
    persona: The Persona class instance
    event_description: Description of the event
  OUTPUT:
    An integer poignancy score (1-10).
  """
  runner = EventPoignancyRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(event_description, test_input=test_input)


# New decomposition schedule prompt
class NewDecompScheduleRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/task_decomp_v2.txt",
      example_output="['wake up and complete the morning routine', 60]",
      special_instruction="Output ONLY a JSON list with task and duration format: ['task name', duration_in_minutes]",
      fail_safe_response=[["waiting", 5]],
      verbose=False
    )

  def create_prompt_input(self, task, time_limit, test_input=None):
    if test_input:
      return test_input

    return [self.persona.scratch.get_str_iss(), task, time_limit, time_limit]

  def func_clean_up(self, gpt_response, prompt=""):
    try:
      return ast.literal_eval(gpt_response.strip())
    except:
      return ["", 5]

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return (isinstance(result, list) and len(result) == 2 and
              isinstance(result[1], int) and result[1] > 0)
    except:
      return False


def run_gpt_prompt_new_decomp_schedule(persona, task, time_limit, test_input=None, verbose=False):
  """
  Creates a new decomposed schedule for a task.

  INPUT:
    persona: The Persona class instance
    task: The task to decompose
    time_limit: Time limit in minutes
  OUTPUT:
    A list of [task_name, duration] pairs.
  """
  runner = NewDecompScheduleRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(task, time_limit, test_input=test_input)


# Convo to thoughts prompt
class ConvoToThoughtsRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/convo_to_thoughts_v1.txt",
      example_output="developing feelings for",
      special_instruction="Output ONLY the reflection, no quotes or formatting.",
      fail_safe_response="thinking about the conversation",
      verbose=False
    )

  def create_prompt_input(self, all_utt, test_input=None):
    if test_input:
      return test_input

    convo_str = ""
    for row in all_utt:
      convo_str += f"{row[0]}: {row[1]}\n"
    return [convo_str]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.strip()

  def func_validate(self, gpt_response, prompt=""):
    return len(gpt_response.strip()) >= 1


def run_gpt_prompt_convo_to_thoughts(persona, all_utt, test_input=None, verbose=False):
  """
  Generates thoughts from a conversation.

  INPUT:
    persona: The Persona class instance
    all_utt: List of [speaker, utterance] pairs
  OUTPUT:
    A thought string based on the conversation.
  """
  runner = ConvoToThoughtsRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(all_utt, test_input=test_input)


# Focal point prompt
class FocalPtRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/generate_focal_pt_v1.txt",
      example_output="1) reflection: What would...",
      special_instruction="Output a numbered list of focal points.",
      fail_safe_response=["reflection"],
      verbose=False
    )

  def create_prompt_input(self, statements, n, test_input=None):
    if test_input:
      return test_input

    return [statements, str(n)]

  def func_clean_up(self, gpt_response, prompt=""):
    cr = gpt_response.strip()
    focal_points = []
    for i in cr.split("\n"):
      focal_points.append(i)
    return focal_points

  def func_validate(self, gpt_response, prompt=""):
    try:
      result = self.func_clean_up(gpt_response, prompt)
      return isinstance(result, list) and len(result) > 0
    except:
      return False


def run_gpt_prompt_focal_pt(persona, statements, n, test_input=None, verbose=False):
  """
  Generates focal points for reflection.

  INPUT:
    persona: The Persona class instance
    statements: Related statements to analyze
    n: Number of focal points to generate
  OUTPUT:
    A list of focal points.
  """
  runner = FocalPtRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(statements, n, test_input=test_input)

# Thought poignancy prompt
class ThoughtPoignancyRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/poignancy_thought_v1.txt",
      example_output="5",
      special_instruction="The output should ONLY contain ONE integer value on the scale of 1 to 10.",
      fail_safe_response=4,
      verbose=False
    )

  def create_prompt_input(self, event_description, test_input=None):
    if test_input:
      return test_input
    return [
      self.persona.scratch.name,
      self.persona.scratch.get_str_iss(),
      self.persona.scratch.name,
      event_description
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return int(gpt_response.strip())


  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError):
      return False


def run_gpt_prompt_thought_poignancy(persona, event_description, test_input=None, verbose=False):
  """
  Computes a poignancy score for the persona's thought (1-10).

  INPUT:
    persona: The Persona class instance
    event_description: The thought to evaluate
  OUTPUT:
    Integer score from 1 to 10.
  """
  runner = ThoughtPoignancyRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(event_description, test_input=test_input)

# Chat poignancy prompt
class ChatPoignancyRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/poignancy_chat_v1.txt",
      example_output="5",
      special_instruction="The output should ONLY contain ONE integer value on the scale of 1 to 10.",
      fail_safe_response=4,
      verbose=False
    )

  def create_prompt_input(self, event_description, test_input=None):
    if test_input:
      return test_input
    return [
      self.persona.scratch.name,
      self.persona.scratch.get_str_iss(),
      self.persona.scratch.name,
      event_description
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return int(gpt_response.strip())

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError):
      return False


def run_gpt_prompt_chat_poignancy(persona, event_description, test_input=None, verbose=False):
  """
  Computes a poignancy score for a chat event (1-10).

  INPUT:
    persona: The Persona class instance
    event_description: The chat event to evaluate
  OUTPUT:
    Integer score from 1 to 10.
  """
  runner = ChatPoignancyRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(event_description, test_input=test_input)
"""
Remaining prompt functions for run_gpt_prompt.py
Complete implementation of the 11 missing functions
"""

# Insight and guidance prompt
class InsightAndGuidanceRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/insight_and_evidence_v1.txt",
      example_output="",
      special_instruction="",
      fail_safe_response=[],
      verbose=False
    )

  def create_prompt_input(self, statements, n, test_input=None):
    if test_input:
      return test_input
    return [statements, str(n)]

  def func_clean_up(self, gpt_response, prompt=""):
    gpt_response = "1. " + gpt_response.strip()
    ret = dict()
    for i in gpt_response.split("\n"):
      row = i.split(". ")[-1]
      if "(because of " in row:
        thought = row.split("(because of ")[0].strip()
        evi_raw = row.split("(because of ")[1].split(")")[0].strip()
        evi_raw = re.findall(r'\d+', evi_raw)
        evi_raw = [int(i.strip()) for i in evi_raw]
      else:
        thought = row.strip()
        evi_raw = []
      ret[thought] = evi_raw
    return ret

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError, IndexError, AttributeError):
      return False

  def get_fail_safe(self):
    return ["I am hungry"]


def run_gpt_prompt_insight_and_guidance(persona, statements, n, test_input=None, verbose=False):
  """
  Generates insights and guidance based on statements.

  INPUT:
    persona: The Persona class instance
    statements: Statements to analyze
    n: Number of insights to generate
  OUTPUT:
    Dictionary mapping insights to evidence.
  """
  runner = InsightAndGuidanceRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(statements, n, test_input=test_input)


# Agent chat summarize ideas prompt
class AgentChatSummarizeIdeasRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/summarize_chat_ideas_v1.txt",
      example_output='Jane Doe is working on a project',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, target_persona, statements, curr_context, test_input=None):
    if test_input:
      return test_input
    return [
      self.persona.scratch.get_str_curr_date_str(),
      curr_context,
      self.persona.scratch.currently,
      statements,
      self.persona.scratch.name,
      target_persona.scratch.name
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError, IndexError, AttributeError):
      return False


def run_gpt_prompt_agent_chat_summarize_ideas(persona, target_persona, statements, curr_context, test_input=None, verbose=False):
  """
  Summarizes ideas from a conversation with another persona.

  INPUT:
    persona: The Persona class instance
    target_persona: The other persona in conversation
    statements: Conversation statements
    curr_context: Current context
  OUTPUT:
    Summary of ideas.
  """
  runner = AgentChatSummarizeIdeasRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, statements, curr_context, test_input=test_input)


# Agent chat summarize relationship prompt
class AgentChatSummarizeRelationshipRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/summarize_chat_relationship_v2.txt",
      example_output='',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, target_persona, statements, test_input=None):
    if test_input:
      return test_input
    return [statements, self.persona.scratch.name, target_persona.scratch.name]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError, IndexError, AttributeError):
      return False


def run_gpt_prompt_agent_chat_summarize_relationship(persona, target_persona, statements, test_input=None, verbose=False):
  """
  Summarizes relationship insights from conversation.

  INPUT:
    persona: The Persona class instance
    target_persona: The other persona
    statements: Conversation statements
  OUTPUT:
    Relationship summary.
  """
  runner = AgentChatSummarizeRelationshipRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, statements, test_input=test_input)


# Summarize ideas prompt
class SummarizeIdeasRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/summarize_ideas_v1.txt",
      example_output='Jane Doe is working on a project',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, statements, question, test_input=None):
    if test_input:
      return test_input
    return [statements, question]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError, IndexError, AttributeError):
      return False


def run_gpt_prompt_summarize_ideas(persona, statements, question, test_input=None, verbose=False):
  """
  Summarizes ideas based on statements and a question.

  INPUT:
    persona: The Persona class instance
    statements: Statements to summarize
    question: Guiding question
  OUTPUT:
    Summary of ideas.
  """
  runner = SummarizeIdeasRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(statements, question, test_input=test_input)
# Agent chat prompt
class AgentChatRunner(GPTPromptRunner):
  def __init__(self, persona, maze):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/agent_chat_v1.txt",
      example_output='["Barack Obama", "Hi Hillary"]\n["Hillary Clinton", "Hi Barack"]\n["Barack Obama", "How are you doing today?"]\n["Hillary Clinton", "I am doing well. Busy with the campaign."]\n["Barack Obama", "It was good seeing you Hillary. Good luck."]\n["Hillary Clinton", "You too Barack."]\n["Barack Obama", "Goodbye Hillary."]',
      special_instruction='The output should be a list of lists, where each inner list is of the format ["<Name>", "<Utterance>"]',
      fail_safe_response=[],
      verbose=False
    )
    self.maze = maze

  def create_prompt_input(self, target_persona, curr_context, init_summ_idea, target_summ_idea, test_input=None):
    if test_input:
      return test_input

    prev_convo_insert = "\n"
    if self.persona.a_mem.seq_chat:
      for i in self.persona.a_mem.seq_chat:
        if i.object == target_persona.scratch.name:
          v1 = int((self.persona.scratch.curr_time - i.created).total_seconds()/60)
          prev_convo_insert += f'{str(v1)} minutes ago, {self.persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation.'
          break
    if prev_convo_insert == "\n":
      prev_convo_insert = ""
    if self.persona.a_mem.seq_chat:
      if int((self.persona.scratch.curr_time - self.persona.a_mem.seq_chat[-1].created).total_seconds()/60) > 480:
        prev_convo_insert = ""

    curr_sector = f"{self.maze.access_tile(self.persona.scratch.curr_tile)['sector']}"
    curr_arena = f"{self.maze.access_tile(self.persona.scratch.curr_tile)['arena']}"
    curr_location = f"{curr_arena} in {curr_sector}"

    return [
      self.persona.scratch.currently,
      target_persona.scratch.currently,
      prev_convo_insert,
      curr_context,
      curr_location,
      self.persona.scratch.name,
      init_summ_idea,
      self.persona.scratch.name,
      target_persona.scratch.name,
      target_persona.scratch.name,
      target_summ_idea,
      target_persona.scratch.name,
      self.persona.scratch.name,
      self.persona.scratch.name
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    gpt_response = (prompt + gpt_response).split("Here is their conversation.")[-1].strip()
    content = re.findall('"([^"]*)"', gpt_response)

    speaker_order = []
    for i in gpt_response.split("\n"):
      name = i.split(":")[0].strip()
      if name:
        speaker_order += [name]

    ret = []
    for count, speaker in enumerate(speaker_order):
      if count < len(content):
        ret += [[speaker, content[count]]]

    return ret

  def func_validate(self, gpt_response, prompt=""):
    try:
      self.func_clean_up(gpt_response, prompt)
      return True
    except (ValueError, TypeError, IndexError, AttributeError, KeyError):
      return False

  def get_fail_safe(self):
    return []


def run_gpt_prompt_agent_chat(maze, persona, target_persona, curr_context, init_summ_idea, target_summ_idea, test_input=None, verbose=False):
  """
  Generates a conversation between two personas.

  INPUT:
    maze: The maze object
    persona: The Persona class instance
    target_persona: The other persona
    curr_context: Current context
    init_summ_idea: Initial summary for persona
    target_summ_idea: Initial summary for target persona
  OUTPUT:
    List of [speaker, utterance] pairs.
  """
  runner = AgentChatRunner(persona, maze)
  if verbose:
    runner.verbose = True
  return runner.run(target_persona, curr_context, init_summ_idea, target_summ_idea, test_input=test_input)

# Generate next conversation line prompt
class GenerateNextConvoLineRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v3_ChatGPT/generate_next_convo_line_v1.txt",
      example_output='Barack Obama is intellectually curious about Hillary Clinton and asks her about her views.',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, interlocutor_desc, prev_convo, retrieved_summary, test_input=None):
    if test_input:
      return test_input
    return [
      prev_convo,
      interlocutor_desc,
      retrieved_summary
    ]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()


def run_gpt_prompt_generate_next_convo_line(persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None, verbose=False):
  """
  Generates the next line in a conversation.

  INPUT:
    persona: The Persona class instance
    interlocutor_desc: Description of interlocutor
    prev_convo: Previous conversation
    retrieved_summary: Summary of retrieved memories
  OUTPUT:
    Next conversation line.
  """
  runner = GenerateNextConvoLineRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(interlocutor_desc, prev_convo, retrieved_summary, test_input=test_input)


# Generate whisper inner thought prompt
class GenerateWhisperInnerThoughtRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/whisper_inner_thought_v1.txt",
      example_output='Barack Obama feels that Hillary Clinton is impressively intellectually curious.',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, whisper, test_input=None):
    if test_input:
      return test_input
    return [self.persona.scratch.name, whisper]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()


def run_gpt_prompt_generate_whisper_inner_thought(persona, whisper, test_input=None, verbose=False):
  """
  Generates inner thought based on whisper.

  INPUT:
    persona: The Persona class instance
    whisper: The whisper to process
  OUTPUT:
    Inner thought.
  """
  runner = GenerateWhisperInnerThoughtRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(whisper, test_input=test_input)


# Planning thought on conversation prompt
class PlanningThoughtOnConvoRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/planning_thought_on_convo_v1.txt",
      example_output='For Barack Obama: focus on the conversation with Hillary Clinton about his ambitions.',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, all_utt, test_input=None):
    if test_input:
      return test_input
    return [all_utt]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()


def run_gpt_prompt_planning_thought_on_convo(persona, all_utt, test_input=None, verbose=False):
  """
  Generates planning thought based on conversation.

  INPUT:
    persona: The Persona class instance
    all_utt: All utterances
  OUTPUT:
    Planning thought.
  """
  runner = PlanningThoughtOnConvoRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(all_utt, test_input=test_input)


# Memo on conversation prompt
class MemoOnConvoRunner(GPTPromptRunner):
  def __init__(self, persona):
    super().__init__(
      persona=persona,
      prompt_template="persona/prompt_template/v2/memo_on_convo_v1.txt",
      example_output='Barack Obama sees that Hillary Clinton is intellectually curious.',
      special_instruction='The output should be a string that responds to the question.',
      fail_safe_response="...",
      verbose=False
    )

  def create_prompt_input(self, all_utt, test_input=None):
    if test_input:
      return test_input
    return [self.persona.scratch.name, all_utt]

  def func_clean_up(self, gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()


def run_gpt_prompt_memo_on_convo(persona, all_utt, test_input=None, verbose=False):
  """
  Generates memo on conversation.

  INPUT:
    persona: The Persona class instance
    all_utt: All utterances
  OUTPUT:
    Memo about conversation.
  """
  runner = MemoOnConvoRunner(persona)
  if verbose:
    runner.verbose = True
  return runner.run(all_utt, test_input=test_input)
