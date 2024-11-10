#!/bin/bash
VENV_DIR=venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
source "${SCRIPT_DIR}/${VENV_DIR}/bin/activate"
python3 "${SCRIPT_DIR}/main.py" "$@"

#@echo off
#REM run.bat
#SET SCRIPT_DIR=%~dp0
#call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
#python main.py %*
