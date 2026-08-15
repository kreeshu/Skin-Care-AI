@echo off
cd /d "%~dp0.."
"venv\Scripts\python.exe" src\model\train_multitask.py --model-dir models >> outputs\train_multitask.log 2>&1
