@echo off
rem Below allows launching chiadog interactively by user while retaining system-wide protection against launching non-interactive scripts
powershell -ExecutionPolicy Bypass -File .\scripts\win64\start_in_venv.ps1