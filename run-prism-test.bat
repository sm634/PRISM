@echo off

set root=%HOMEPATH%\AppData\Local\anaconda3
call %root%\Scripts\activate.bat
call conda activate prism_env
cd PRISM_SCRIPT=%HOMEPATH%\data-science-projects\ED-A\PRISM\

call streamlit run main.py --server.port 8501
exit 0