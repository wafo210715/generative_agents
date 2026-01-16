"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: print_prompt.py
Description: For printing prompts when the setting for verbose is set to True.
"""
import sys
sys.path.append('../')

import json
import numpy
import datetime
import random

from global_methods import *
from persona.prompt_template.gpt_structure import *
from utils import *

##############################################################################
#                    PERSONA Chapter 1: Prompt Structures                    #
##############################################################################

def print_run_prompts(prompt_template=None,
                      persona=None,
                      example_output=None,
                      special_instruction=None,
                      prompt_input=None,
                      prompt=None,
                      output=None):
  print (f"=== {prompt_template}")
  print ("~~~ persona    ---------------------------------------------------")
  print (getattr(persona, 'name', getattr(persona.scratch, 'name', 'Unknown')), "\n")
  print ("~~~ example_output ------------------------------------------------")
  print (example_output, "\n")
  print ("~~~ special_instruction -------------------------------------------")
  print (special_instruction, "\n")
  print ("~~~ prompt_input    ----------------------------------------------")
  print (prompt_input, "\n")
  print ("~~~ prompt    ----------------------------------------------------")
  print (prompt, "\n")
  print ("~~~ output    ----------------------------------------------------")
  print (output, "\n")
  print ("=== END ==========================================================")
  print ("\n\n\n")
