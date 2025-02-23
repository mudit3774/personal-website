#!/bin/bash

# Kill any existing Python processes running on port 5006
lsof -ti:5006 | xargs kill -9 2>/dev/null || true

# Start the Flask server
python3 api.py
