@echo off
setlocal
set "FC=D:\FreeCAD\FreeCAD_1.1.4-Windows-x86_64-py311\bin\freecadcmd.exe"
set "ROOT=%~dp0"
cd /d "%ROOT%"
"%FC%" "%ROOT%run_tests.py"
endlocal