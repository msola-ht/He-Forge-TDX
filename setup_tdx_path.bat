@echo off
setlocal
cd /d "%~dp0"
call :resolve_python
if errorlevel 1 goto end

:start
cls
echo ========================================
echo TDX Path Setup
echo ========================================
echo.
echo Python: %PYTHON_EXE%
echo [1/2] Diagnose current path and connectivity
"%PYTHON_EXE%" scripts\diagnose_tdx_path.py --probe stock_list --market 5 --show-candidates --output raw
echo.
echo [2/2] List selectable candidates
"%PYTHON_EXE%" scripts\setup_tdx_path.py --output raw
echo.
echo Input a candidate index to save it.
echo Input M for manual path.
echo Input R to run detection again.
echo Input 0 to exit.
echo.
set /p action=Select action:

if "%action%"=="0" goto end
if /I "%action%"=="R" goto start
if /I "%action%"=="M" goto manual

"%PYTHON_EXE%" scripts\setup_tdx_path.py --pick %action% --output raw
goto verify

:manual
echo.
set /p userdir=Enter full PYPlugins/user path:
if "%userdir%"=="" goto start
"%PYTHON_EXE%" scripts\setup_tdx_path.py --user-dir "%userdir%" --output raw

:verify
echo.
echo Re-check connectivity after save
"%PYTHON_EXE%" scripts\diagnose_tdx_path.py --probe stock_list --market 5 --output raw
echo.
pause
goto start

:resolve_python
set "PYTHON_EXE="
if defined TDX_PYTHON if exist "%TDX_PYTHON%" set "PYTHON_EXE=%TDX_PYTHON%"
if not defined PYTHON_EXE if defined CONDA_PREFIX if exist "%CONDA_PREFIX%\python.exe" set "PYTHON_EXE=%CONDA_PREFIX%\python.exe"
if not defined PYTHON_EXE if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%USERPROFILE%\miniforge3\envs\main\python.exe" set "PYTHON_EXE=%USERPROFILE%\miniforge3\envs\main\python.exe"
if not defined PYTHON_EXE if exist "%LocalAppData%\miniforge3\envs\main\python.exe" set "PYTHON_EXE=%LocalAppData%\miniforge3\envs\main\python.exe"
if not defined PYTHON_EXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=python"
)
if not defined PYTHON_EXE (
  echo Python not found.
  echo Set TDX_PYTHON to the target python.exe and retry.
  pause
  exit /b 1
)
exit /b 0

:end
endlocal
