#!/bin/bash
cd /Users/guanhongli/Documents/repositories-github/generative_agents/reverie/backend_server
echo "base_the_ville_isabella_maria_klaus" | "/Users/guanhongli/Documents/repositories-github/generative_agents/venv/bin/python" reverie.py
echo "test-migration-0115" | "/Users/guanhongli/Documents/repositories-github/generative_agents/venv/bin/python" reverie.py 2>&1 | head -50
