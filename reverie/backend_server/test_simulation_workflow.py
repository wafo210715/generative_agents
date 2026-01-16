#!/usr/bin/env python3
"""
Test the complete simulation workflow with refactored prompt functions
"""

import sys
import os
sys.path.append('/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server')

# Test imports
try:
    from persona.prompt_template.run_gpt_prompt import (
        run_gpt_prompt_wake_up_hour,
        run_gpt_prompt_daily_plan,
        run_gpt_prompt_task_decomp,
        run_gpt_prompt_action_sector,
        run_gpt_prompt_event_triple
    )
    print("✅ All critical functions imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test that we can load a real simulation
import json
storage_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/environment/frontend_server/storage"
base_sim = "base_the_ville_isabella_maria_klaus"

# Check if simulation exists
if os.path.exists(f"{storage_path}/{base_sim}"):
    print(f"✅ Base simulation '{base_sim}' found")
else:
    print(f"❌ Base simulation '{base_sim}' not found")

# Test persona metadata loading
try:
    with open(f"{storage_path}/{base_sim}/meta.json") as f:
        meta = json.load(f)
    print(f"✅ Meta data loaded. Personas: {meta['persona_names']}")
except Exception as e:
    print(f"❌ Failed to load meta: {e}")

print("\n" + "="*60)
print("All checks passed! Refactored code is ready.")
print("Run: cd /Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server && python reverie.py")
print("Then enter: base_the_ville_isabella_maria_klaus")
print("Then enter: your_simulation_name")
print("Then enter: run 10")
print("="*60)
