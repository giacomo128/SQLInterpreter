#!/bin/bash

set -e

echo "--- Installing dependencies: ---"
python3 -m pip install lark > log.txt
python3 -m pip install pytest >> log.txt
echo "--- Finished installation process ---"
echo ""
echo "--- Program output ---"

python3 src/main.py "$@"