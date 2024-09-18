#!/bin/bash

set -e

echo "Nuking any pre-existing virtual environment."
echo "(also, please deactivate any active environments if you have any)"

rm -rf ./venv
python3 -m venv ./venv

echo "Loading mpbn from current implementation"
./venv/bin/pip install ..

echo "Running models for up to one minute using dnf-bench.py."
./venv/bin/python3 run.py 1m bbm-bnet dnf-bench.py
./venv/bin/python3 run.py 1m hard-multi-valued dnf-bench.py

echo "Saving results into a zip file."
zip -r current.zip _run_*

# Clean up.
rm -rf _run_*
rm -rf ./venv