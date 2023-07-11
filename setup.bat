@echo off
set root=%HOMEPATH%\AppData\Local\miniconda3
call %root%\Scripts\activate.bat %root%

if exist %root%\envs\prism_env\ (
	echo The environment already exists. Removing it and reinstalling.
	call conda env remove -n prism_env
	timeout 3
	call conda env create -f environment.yaml
	call conda activate prism_env
) else (
	call conda env create -f environment.yaml
	call conda activate prism_env
)

set PYTHON_EXECUTER=%HOMEPATH%\AppData\Local\miniconda3\envs\prism_env\python.exe
set PRISM_SETUP=%HOMEPATH%\repos\PRISM\setup\nltk-packages.py

%PYTHON_EXECUTER% %PRISM_SETUP%
echo The set up is complete.

pause