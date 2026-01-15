# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Generative Agents is a research project that simulates believable human behaviors using LLM-powered computational agents. The system creates an interactive simulation called "Smallville" where AI agents live virtual lives, form relationships, and exhibit emergent social behaviors through LLM-based reasoning and memory systems.

## Common Development Commands

### Running the Simulation

**Environment Server (Django):**
```bash
cd environment/frontend_server
python manage.py runserver
```
Access at http://localhost:8000

**Simulation Server:**
```bash
# First create required utils.py in reverie/backend_server (see Setup section)
cd reverie/backend_server
python reverie.py
# When prompted: Enter base simulation name (e.g., base_the_ville_isabella_maria_klaus)
# Then enter new simulation name
```

**Simulation Controls:**
- `run <steps>` - Run simulation for N steps (10 seconds/step)
- `fin` - Save and exit
- `exit` - Exit without saving
- `call -- load history <path>` - Load agent history from CSV

**Viewing Simulations:**
- Replay: http://localhost:8000/replay/<sim-name>/<step>/
- Demo: http://localhost:8000/demo/<sim-name>/<step>/<speed>/ (speed: 1-5)

### Setup Requirements

**Initial Setup:**
1. Create `reverie/backend_server/utils.py` with:
```python
openai_api_key = "<Your OpenAI API>"
key_owner = "<Name>"
maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"
fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"
collision_block_id = "32125"
debug = True
```

2. Install requirements:
```bash
pip install -r requirements.txt  # from root
pip install -r environment/frontend_server/requirements.txt
```

**Python Version:** Tested on Python 3.9.12

## Architecture Overview

### Two-Server Architecture
- **Environment Server (Django)**: Visual frontend and storage layer
- **Simulation Server (reverie.py)**: Core AI logic and agent runtime
- Servers communicate through file system and Django views

### Core Components

**reverie/backend_server/**
- `reverie.py`: Main simulation controller
- `maze.py`: Environment/map handling with collision detection
- `persona/`: Core agent implementation
  - `persona.py`: Agent orchestration
  - `memory_structures/`: Memory system (associative, scratch, spatial)
  - `cognitive_modules/`: LLM-based reasoning (perception, retrieval, planning, execution, conversation, reflection)
  - `prompt_template/`: GPT-3.5 prompts for different cognitive functions

**environment/frontend_server/**
- Django web application for visualization
- `storage/`: Persistent simulation data and configurations
- `static_dirs/`: Game assets, maps, and character sprites
- `translator/`: Django views for translating sim state to frontend

### Agent Architecture
1. **Memory System**: Three-tier memory (short-term scratch, medium-term associative, spatial)
2. **Cognitive Modules**: LLM-powered reasoning for different aspects of behavior
3. **Plan-Execute Cycle**: Agents create daily plans, then reason about next actions
4. **Conversational Pairs**: Agents converse in pairs through structured dialogue system

## Development Notes

- **No test suite**: Only 2 minimal test files exist - manual testing through simulation interface
- **Research code**: Academic prototype, not production quality
- **LLM-dependent**: Requires OpenAI API key - no local model support
- **Stateful**: Heavy reliance on file system for state persistence
- **Manual configuration**: No automated setup - must follow manual steps
- **Storage-heavy**: Generates substantial JSON/CSV data in storage/

## Key Files
- `reverie/backend_server/utils.py`: Configuration (must create manually)
- `reverie/backend_server/reverie.py`: Main simulation entry point
- `reverie/backend_server/persona/persona.py`: Core agent logic
- `environment/frontend_server/translator/views.py`: Environment-Django interfaces
