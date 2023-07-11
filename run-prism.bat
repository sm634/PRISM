@echo off
set PYTHON_EXECUTER=%HOMEPATH%\AppData\Local\miniconda3\envs\prism_env\python.exe

set PRISM_SCRIPT=%HOMEPATH%\repos\PRISM\main.py

%PYTHON_EXECUTER% %PRISM_SCRIPT%
pause