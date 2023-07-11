@echo off
set PYTHON_EXECUTER=%HOMEPATH%\AppData\Local\miniconda3\envs\prism_env\python.exe

set COST_SCRIPT=%HOMEPATH%\repos\PRISM\calculate_cost.py

%PYTHON_EXECUTER% %COST_SCRIPT%
pause