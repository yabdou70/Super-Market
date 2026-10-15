@echo off
title Price Comparison Dashboard Runner
cd /d D:\AI_agent
call venv311\Scripts\activate.bat
python -m streamlit run price_dashboard.py
pause