# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎉 Current Status (January 17, 2026)

**✅ LLM Integration Complete**: DeepSeek and Kimi providers fully integrated
- **DeepSeek-Reasoner**: Reflection & planning (~30s/call)
- **DeepSeek-Chat**: Conversations & actions (~5s/call)
- **Kimi K2**: Alternative provider support

**✅ Code Refactoring**: Massive 42% code reduction achieved
- 32 prompt functions refactored with GPTPromptRunner base class
- Eliminated code duplication, improved maintainability
- All tests passing, simulation running successfully

**✅ Active Development Areas**:
- Simulation performance optimization (first run: 5-10min)
- API key security enhancement (environment variables)
- Web UI integration improvements

## Critical Fixes (2025-01-17)

**✅ Fixed OpenAI API Version Incompatibility**
- **Issue**: `reverie.py` failed with "module 'openai' has no attribute 'OpenAI'"
- **Root Cause**: Virtual environment had `openai==0.27.0` (legacy API) but code uses v1.x+ syntax
- **Fix**: Upgraded `openai` to version **2.15.0** in venv
- **Impact**: Both `chat.completions.create()` and `embeddings.create()` now work correctly

**✅ Fixed Import Path Error** (gpt_structure.py)
- **Issue**: `from utils import ...` failed when running from directories other than `reverie/backend_server/`
- **Root Cause**: Absolute path not in sys.path
- **Fix**: Added path manipulation to automatically add `reverie/backend_server` to sys.path
- **Impact**: Imports now work from any directory

**✅ Fixed IndexError** (run_gpt_prompt.py)
- **Issue**: `ActionSectorRunner.get_fail_safe()` crashed with `IndexError: tuple index out of range`
- **Root Cause**: Code tried to access `self.persona.scratch.curr_tile[2]` but curr_tile doesn't have that index
- **Fix**: Refactored to store `maze` as instance variable and use `maze.access_tile()` instead
- **Impact**: Simulation now runs without crashing on sector determination

**✅ Migrated to Modern OpenAI API** (gpt_structure.py)
- **Changes**:
  - `openai.ChatCompletion.create()` → `client.chat.completions.create()`
  - `openai.Embedding.create()` → `client.embeddings.create()`
  - Response access: `response['data'][0]['embedding']` → `response.data[0].embedding`
  - Client created per-request with proper base_url handling

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

**Initial Setup - LLM Provider Configuration:**
1. Create `reverie/backend_server/utils.py`. Example configurations:

**For DeepSeek (Recommended - Cheap and Good):**
```python
active_provider = "deepseek"
openai_api_key = "sk-your-deepseek-key"
```

**For OpenAI:**
```python
active_provider = "openai"
openai_api_key = "sk-your-openai-key"
```

**For Kimi:**
```python
active_provider = "kimi"
openai_api_key = "sk-your-kimi-key"
```

**Optional: Add New Provider - Update LLM_PROVIDERS dict:**
```python
LLM_PROVIDERS = {
    ...
    "myprovider": {
        "base_url": "https://api.myprovider.com/v1",
        "chat_model": "my-chat-model",
        "reasoner_model": "my-reasoner-model",
        "embedding_model": None
    }
    ...
}
```

**Common settings:**
```python
key_owner = "Your Name"
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

## LLM Integration Notes

### Updated System (2025-01-15)

**Fixed Issues:**
- ✅ No more "TOKEN LIMIT EXCEEDED" errors - all API calls now use modern chat format
- ✅ Removed hardcoded temperature - uses model defaults (DeepSeek: 1.0, Kimi: 0.6)
- ✅ Embedding model fully integrated from utils.py configuration
- ✅ Legacy GPT-3 API calls removed, all use unified `llm_chat_request()`

**Model Configuration by Category:**

**1. Reasoner Models** (for reflection, planning, deep thinking):
```python
reasoner_models = {
    "DeepSeek/DeepSeek-Reasoner": {
        "model_id": "deepseek-reasoner",
        "api_key": "YOUR_KEY_HERE",
        "api_base_url": "https://api.deepseek.com",
        "model_format": "openai",
        "is_valid": True  # Enable/disable easily
    }
}
```

**2. Chat Models** (for conversations, actions):
```python
chat_models = {
    "DeepSeek/DeepSeek-Chat": {
        "model_id": "deepseek-chat",
        "api_key": "YOUR_KEY_HERE",
        "api_base_url": "https://api.deepseek.com",
        "is_valid": True
    }
}
```

**3. Embedding Models** (for vectorizing memories):
```python
embedding_models = {
    "WeaveX/text-embedding-3-small": {
        "model_id": "text-embedding-3-small",
        "api_key": "YOUR_KEY_HERE",
        "api_base_url": "https://openai.weavex.tech",
        "is_valid": True
    }
}
```

### Key Implementation Improvements

**1. Unified LLM Interface (`gpt_structure.py`)**
```python
def llm_chat_request(prompt, model_type="chat"):
    """Unified interface for all LLM providers"""
    # Uses model defaults, no hardcoded temperature
    # Supports: OpenAI, DeepSeek, Kimi, custom endpoints
```

**2. Safe Response Function**
```python
def llm_safe_generate_response(prompt, model_type="chat", ...):
    """Modern error handling with retry logic"""
    # Uses llm_chat_request, not legacy GPT-3 API
    # JSON validation and cleanup
```

**3. Dynamic Model Selection**
```python
def get_active_model_config(model_type="chat"):
    """Auto-selects enabled model from config"""
    # Checks is_valid flag
    # Returns config dict for API calls
```

### Running DeekSeek Simulation

**Step 1: Configure API Keys**
```bash
cd reverie/backend_server
# Edit utils.py with your API keys
# DeepSeek: Get key from https://platform.deepseek.com/api_keys
# WeaveX: Use your embedding model key
```

**Step 2: Test Configuration**
```bash
source ../../venv/bin/activate
python test_providers.py
```

**Step 3: Start Simulation**
```bash
# Terminal 1 - Django visualization
python manage.py runserver

# Terminal 2 - Agent simulation
python reverie.py
```

**Configuration File:**
```bash
cat reverie/backend_server/utils.py  # Contains all model configs
```

### Persona Encoding System

Agents are JSON-encoded in `bootstrap_memory/scratch.json`:

```json
{
  "name": "Isabella Rodriguez",
  "innate": "friendly, outgoing, hospitable",
  "learned": "Isabella is a cafe owner...",
  "currently": "planning Valentine's Day party...",
  "lifestyle": "goes to bed around 11pm, awakes around 6am",
  "living_area": "cafe",
  "daily_req": [...],
  "curr_tile": [58, 95]
}
```

**Creating New Personas:**
1. Copy existing persona folder
2. Edit `scratch.json` traits
3. Update location in `spatial_memory.json`
4. Set initial memories in `associative_memory/`
5. Update `meta.json` with new names

**Agent Initialization Process:**
1. Load `meta.json` for persona names
2. Read each `bootstrap_memory/scratch.json`
3. Initialize spatial and associative memory
4. Place agents at specified coordinates
5. Start cognitive loop (perceive → retrieve → plan → execute)

### Conversation JSON Format

**Required Format:**
```json
[
  ["Speaker Name", "Utterance text"],
  ["Speaker Name", "Utterance text"]
]
```

**Why JSON?**
- Frontend parses to display agent interactions
- Memory system stores structured conversations
- Reflection modules analyze social patterns
- Retrieved and used in future conversations

**Validation:**
- Checks for valid JSON array
- Validates each item is [string, string]
- Falls back to fail-safe response if invalid

### Performance Notes

**DeepSeek Model Performance:**
- **DeepSeek-Reasoner**: ~30 seconds for complex reflection/planning
- **DeepSeek-Chat**: ~5 seconds per conversation turn
- **text-embedding-3-small**: ~1 second per embedding

**Speed Optimization:**
- Currency: Use DeepSeek-Chat for routine actions
- Planning: Use DeepSeek-Reasoner for hourly/daily planning
- Reflection: Use DeepSeek-Reasoner every 3-5 steps only

**Cost Efficiency:**
- DeepSeek-Chat: $0.07 per 1M tokens (cheap for conversations)
- DeepSeek-Reasoner: $0.14 per 1M tokens (worth it for quality)
- Embedding model: $0.02 per 1M tokens

### API Key Security

**All keys stored in:** `reverie/backend_server/utils.py`

**Safety Features:**
- File in `.gitignore` (line 1) - never committed to GitHub
- Separate per-model configurations
- Easy to swap providers without code changes
- Placeholder text clearly marks where to add keys

**Never commit:** Your actual API keys! Always use placeholder text in public repositories.

## Quick Start

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure API keys
cp reverie/backend_server/utils_template.py \
   reverie/backend_server/utils.py
# Edit utils.py with your keys

# 3. Test
python reverie/backend_server/test_providers.py

# 4. Run
cd environment/frontend_server && python manage.py runserver
cd reverie/backend_server && python reverie.py
```

## Key Files
- `reverie/backend_server/utils.py`: LLM provider configuration
- `reverie/backend_server/persona/prompt_template/gpt_structure.py`: Unified LLM interface
- `reverie/backend_server/test.py`: LLM test script
- `reverie/backend_server/reverie.py`: Main simulation entry point
- `reverie/backend_server/persona/persona.py`: Core agent logic
- `environment/frontend_server/translator/views.py`: Environment-Django interfaces

## Web UI Configuration Interface

A configuration page has been created at `/simulation_config/` to help set up simulations through a web interface.

**Features:**
- Dropdown selection of base simulations
- Input for new simulation names
- Step count slider (1-100 steps)
- Speed selection (1x, 2x, 5x)
- Custom history file upload
- Agent creator form for new personas
- API endpoint to receive configuration

**Current Implementation Status:**
- ✅ HTML template created: `environment/frontend_server/templates/simulation_config.html`
- ✅ Django URL routing added
- ✅ View functions implemented
- ✅ JavaScript API integration
- ✅ Landing page quick-start links

**Known Limitation:** The web UI currently assists with configuration but requires manual backend interaction. After submitting the form, users must still:
1. Manually run `python reverie.py`
2. Enter the same fork/new simulation names when prompted
3. Type `run <steps>` to start the simulation

**Usage:**
```bash
cd environment/frontend_server
python manage.py runserver
# Open http://localhost:8000/
# Click "Configure New Simulation"
```

## TODO: Critical Issues to Address

### High Priority - Web UI Integration
1. **Auto-start backend simulation**: Web UI should automatically trigger backend simulation start
   - Need inter-process communication between Django and reverie.py
   - Could use file-based signals or a small REST API on the backend
   - Goal: Click "Start" in web UI → simulation runs automatically

2. **Backend status monitoring**: Web UI should show if backend is running
   - Display backend status (running/stopped/error)
   - Show current simulation progress
   - Allow pausing/resuming from web UI

### High Priority - Simulation Viewer
3. **Fix agent movement visibility**: Agents appear stationary in viewer even when simulating
   - Investigate `/simulator_home` endpoint
   - Check if movement data is being loaded properly
   - Verify JSON format matches expected structure

4. **Improve map navigation**: Current arrow-key navigation is limiting
   - Add zoom/pan controls to see full map
   - Consider mini-map or overview mode
   - Allow click-to-center on specific agents

5. **Fix "Please set up backend" error**: User sees this when trying to view simulations
   - Error occurs at `/simulator_home` when backend not running
   - Should show helpful message explaining how to start backend
   - Link to web UI configuration page

### Medium Priority - Persona System
6. **Document persona creation**: Add guide to README.md
   - Explain using history files (CSV format)
   - Explain creating base simulations manually
   - Show persona structure and fields
   - Link from web UI agent creator

7. **Web UI agent creation**: Enable creating personas directly from web UI
   - Save agent configuration to proper format
   - Create bootstrap_memory files automatically
   - Allow preview before saving

### Low Priority - Simulation Controls
8. **Real-time speed adjustment**: Allow changing simulation speed during runtime
   - Currently set at startup only
   - Could be adjusted via web UI controls

9. **Step-by-step debugging**: Add ability to step through simulation one action at a time
   - Useful for development and testing
   - Show what each agent is thinking/doing

## TODO: Remaining LLM Integration Steps

### ✅ Completed (2025-01-16)
1. **LLM Provider Integration**: ✅ DeepSeek and Kimi providers fully integrated
   - DeepSeek-Reasoner for reflection/planning (~30s per call)
   - DeepSeek-Chat for conversations (~5s per call)
   - Unified interface in `gpt_structure.py`

2. **Code Refactoring**: ✅ 32 prompt functions refactored to use GPTPromptRunner base class
   - 42% code reduction (2845 → 1650 lines)
   - Eliminated massive code duplication
   - Standardized error handling and validation

3. **Template Files**: ✅ All 23 prompt templates verified and working
   - Fixed path mismatches (daily_planning_v6, task_decomp_v3, etc.)
   - All templates load correctly

4. **Testing**: ✅ Full test suite passing
   - All 32 functions import correctly
   - Mock tests successful
   - Integration test: agents behaving intelligently

### 🔄 In Progress
1. **API Key Security**: Move from hardcoded to environment variables
   - Currently keys are in utils.py (already in .gitignore)
   - Recommended: Use `export DEEPSEEK_API_KEY="sk-..."`

2. **Performance Optimization**:
   - First run can take 5-10+ minutes for initial agent setup
   - Subsequent steps are faster (1-2 min per 10 steps)
   - Consider implementing request batching for speed

### 📋 Remaining (Optional Enhancements)
1. **Error Message Handling**: Update to recognize provider-specific errors
   - DeepSeek rate limiting
   - Network timeout handling
   - Better retry logic

2. **Provider Fallback**: Auto-switch providers if primary fails
   - Primary: DeepSeek-Reasoner (quality)
   - Fallback: Kimi K2 (availability)

3. **Web UI Integration**: Enhance web interface
   - Show backend status (running/stopped/error)
   - Display current simulation step
   - Add pause/resume controls

### 🎯 Quick Start for New Users
```bash
# 1. Setup API Keys
cd reverie/backend_server
# Edit utils.py and add your API keys to chat_models/reasoner_models

# 2. Run Django frontend
cd ../../environment/frontend_server
python manage.py runserver

# 3. Run backend simulation (new terminal)
cd ../../reverie/backend_server
source ../../venv/bin/activate
python reverie.py
# Enter: July1_the_ville_isabella_maria_klaus-step-3-12
# Enter: your_simulation_name
# Enter: run 10

# 4. View simulation
# Replay: http://localhost:8000/replay/your_simulation_name/1/
# Demo: http://localhost:8000/demo/your_simulation_name/1/1/
```
