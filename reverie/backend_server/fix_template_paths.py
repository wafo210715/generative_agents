#!/usr/bin/env python3
"""
Script to fix template paths in run_gpt_prompt.py
Ensures all template paths match the exact files available
"""

import os
import re

# Template path mappings based on what we found
TEMPLATE_FIXES = {
    # Find the correct version of each template
    "daily_planning_v1.txt": "daily_planning_v6.txt",  # Original uses v6
    "task_decomp_v2.txt": "task_decomp_v3.txt",       # Remove v2, keep v3
    # # These might also need fixing
    # "decide_to_react_v1.txt": None,  # Check if exists
    # "poignancy_thought_v1.txt": None,
}

def get_available_templates():
    """Get list of available template files"""
    templates_dir = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/v2"
    available = []
    for file in os.listdir(templates_dir):
        if file.endswith('.txt'):
            available.append(file)
    return available

def analyze_template_usage():
    """Analyze which templates are referenced in the code"""
    file_path = "/Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server/persona/prompt_template/run_gpt_prompt.py"

    with open(file_path, 'r') as f:
        content = f.read()

    # Find all template references
    pattern = r'prompt_template\s*=\s*"persona/prompt_template/v2/([^"]+)"'
    matches = re.findall(pattern, content)

    print("Templates referenced in code:")
    for template in sorted(set(matches)):
        print(f"  - {template}")

    return matches

if __name__ == "__main__":
    print("=" * 60)
    print("Template Path Verification")
    print("=" * 60)

    available = get_available_templates()
    print(f"\nAvailable templates ({len(available)}):")
    for template in sorted(available):
        print(f"  - {template}")

    print("\n" + "=" * 60)
    referenced = analyze_template_usage()

    # Check for missing templates
    missing = []
    for template in referenced:
        if template not in available:
            missing.append(template)

    if missing:
        print(f"\n❌ Missing templates ({len(missing)}):")
        for template in missing:
            print(f"  - {template}")
    else:
        print("\n✅ All referenced templates exist!")
