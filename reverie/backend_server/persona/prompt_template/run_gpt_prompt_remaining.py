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
EOF