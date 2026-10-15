@echo off
cd /d D:\AI_agent
call venv311\Scripts\activate

@echo off
title Price Comparison Dashboard Runner
cd /d D:\AI_agent
call venv311\Scripts\activate.bat
python -m streamlit run app_dashboard.py
pause