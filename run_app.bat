@echo off

rem Check if venv exists
if not exist venv (
    rem Create venv
    python -m venv venv
)

rem Activate venv
call venv\Scripts\activate.bat

rem Install requirements
pip install -r requirements.txt

rem Run app.py
python backend\app.py