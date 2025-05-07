@echo off
REM Run the GUI application (GUI.py) using pythonw if available, else fallback to python
SETLOCAL
SET SCRIPT_DIR=%~dp0
IF EXIST "%SCRIPT_DIR%pythonw.exe" (
    "pythonw.exe" "%SCRIPT_DIR%GUI.py"
) ELSE (
    python "%SCRIPT_DIR%GUI.py"
)
ENDLOCAL 