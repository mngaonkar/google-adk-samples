#!/bin/bash

# Add parent directory to PYTHONPATH so sdk can be imported
export PYTHONPATH="${PYTHONPATH}:$(dirname $(dirname $(realpath $0)))"

python -m agent_graph 
