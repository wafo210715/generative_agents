"""
Author: Joon Sung Park (joonspk@stanford.edu)
Modified for multi-LLM provider support

File: gpt_structure.py
Description: Wrapper functions for calling LLM APIs (DeepSeek, Kimi, etc.)
"""
import json
import openai
import time

from utils import chat_models, reasoner_models, embedding_models

def temp_sleep(seconds=0.1):
  time.sleep(seconds)

def get_active_model_config(model_type="chat"):
  """
  Get the configuration for the active model based on type.
  model_type: "chat" or "reasoner"
  """
  if model_type == "reasoner":
    models_dict = reasoner_models
  else:
    models_dict = chat_models

  # Find the first valid model
  for model_name, config in models_dict.items():
    if config.get("is_valid", False):
      return config

  # Fallback to first model in the dictionary
  first_model = list(models_dict.values())[0]
  return first_model

def setup_openai_client(model_config):
  """
  Configure OpenAI client with the given model configuration.
  """
  openai.api_key = model_config["api_key"]
  openai.api_base = f"{model_config['api_base_url']}/v1"
  openai.api_type = "open_ai"

# Unified LLM chat interface
def llm_chat_request(prompt, model_type="chat"):
  """
  Unified LLM interface that works with any provider (OpenAI, DeepSeek, etc.)
  Uses model's default temperature (no manual temperature setting)
  model_type: "chat" or "reasoner"
  """
  temp_sleep()

  # Get model configuration
  model_config = get_active_model_config(model_type)

  # Setup OpenAI client with model-specific config
  setup_openai_client(model_config)

  try:
    completion = openai.ChatCompletion.create(
      model=model_config["model_id"],
      messages=[{"role": "user", "content": prompt}]
      # No temperature parameter - use model's default
    )
    return completion.choices[0].message.content

  except Exception as e:
    provider_name = model_config.get("api_base_url", "unknown").split("//")[-1].split("/")[0]
    print(f"{provider_name} ERROR: {e}")
    return f"{provider_name} ERROR"

# Legacy wrapper functions that now use our unified interface
def ChatGPT_single_request(prompt):
  """Legacy function - now uses unified LLM interface"""
  return llm_chat_request(prompt)

def ChatGPT_request(prompt):
  """Legacy function - now uses unified LLM interface with error handling"""
  return llm_chat_request(prompt)

def GPT4_request(prompt):
  """Legacy function - now uses reasoner model if available"""
  return llm_chat_request(prompt, model_type="reasoner")


def llm_safe_generate_response(prompt,
                                   example_output,
                                   special_instruction,
                                   model_type="chat",
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False):
  """
  Unified safe response function using modern LLM API.
  Uses llm_chat_request instead of legacy GPT_request.
  """
  prompt = '"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose:
    print ("LLM PROMPT")
    print (prompt)

  for i in range(repeat):
    try:
      curr_gpt_response = llm_chat_request(prompt, model_type=model_type).strip()
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]

      if func_validate(curr_gpt_response, prompt=prompt):
        return func_clean_up(curr_gpt_response, prompt=prompt)

      if verbose:
        print (f"---- repeat count: {i}")
        print (curr_gpt_response)
        print ("~~~~")

    except Exception as e:
      if verbose:
        print(f"Parse error: {e}")
      continue

  return fail_safe_response

# Legacy wrappers - now use unified function
def GPT4_safe_generate_response(prompt, *args, **kwargs):
  """Legacy wrapper - now uses unified LLM interface with reasoner model"""
  return llm_safe_generate_response(prompt, model_type="reasoner", *args, **kwargs)

def ChatGPT_safe_generate_response(prompt, *args, **kwargs):
  """Legacy wrapper - now uses unified LLM interface with chat model"""
  return llm_safe_generate_response(prompt, model_type="chat", *args, **kwargs)


def ChatGPT_safe_generate_response_OLD(prompt, 
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 
    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print (f"---- repeat count: {i}")
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass
  print ("FAIL SAFE TRIGGERED") 
  return fail_safe_response








def generate_prompt(curr_input, prompt_lib_file):
  """
  Takes in the current input (e.g. comment that you want to classifiy) and
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this
  function replaces this substr with the actual curr_input to produce the
  final promopt that will be sent to the GPT3 server.
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file.
  RETURNS:
    a str prompt that will be sent to OpenAI's GPT server.
  """
  if type(curr_input) == type("string"):
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt:
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()


def get_embedding(text):
  """
  Get embedding for text using the configured embedding model from utils.py.
  """
  text = text.replace("\n", " ")
  if not text:
    text = "this is blank"

  # Use configured embedding model from utils.py
  embedding_config = None
  for name, config in embedding_models.items():
    if config.get("is_valid", False):
      embedding_config = config
      break

  if not embedding_config:
    # Fallback: return dummy vector if no embeddings available
    import numpy as np
    dummy_vector = np.random.rand(1536).tolist()
    return dummy_vector

  # Use configured embedding model
  try:
    openai.api_key = embedding_config["api_key"]
    openai.api_base = f"{embedding_config['api_base_url']}/v1"
    openai.api_type = "open_ai"

    response = openai.Embedding.create(
      input=[text],
      model=embedding_config["model_id"]
    )
    return response['data'][0]['embedding']
  except Exception as e:
    print(f"Embedding ERROR: {e}")
    # Fallback to dummy vector
    import numpy as np
    dummy_vector = np.random.rand(1536).tolist()
    return dummy_vector




















