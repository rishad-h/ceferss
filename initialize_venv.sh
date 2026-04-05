#!/bin/bash

# Initialize a virtual environment and install dependencies.

cd "$(dirname "$0")" || exit

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Done. Run 'source venv/bin/activate' to activate the virtual environment."
