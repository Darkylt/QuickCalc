@echo off
rem Activate virtual environment
call .venv\Scripts\activate

rem Build the project
python src/build.py

pause