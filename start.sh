#!/bin/sh
echo "Starting..."
if [ ! -d ".venv" ]; then
    echo "Setting up for the first time..."
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
else
    . .venv/bin/activate
fi
python3 ui.py