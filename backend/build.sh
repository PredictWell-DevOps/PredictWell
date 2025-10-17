#!/usr/bin/env bash
# Diagnostic build script for Render when Root Directory = backend/
# Prints working directory and files, then installs requirements.
set -euo pipefail

python -c "import os,sys; print('CWD='+os.getcwd()); print('FILES='+','.join(sorted(os.listdir('.')))); print('PY='+sys.executable)"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
