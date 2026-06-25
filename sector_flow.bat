@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
call :resolve_python
if errorlevel 1 goto end

:menu
cls
echo ========================================
echo Sector Money Flow Launcher
echo ========================================
echo Python: %PYTHON_EXE%
echo 1. Watch 3 markets with main+buy batch plots every 5 rounds
echo 2. Watch market 16
echo 3. Watch market 17
echo 4. Watch market 18
echo 5. Test 3 markets out of session
echo 6. Watch 3 markets with batch plots every 2 rounds
echo 7. Show 3-market status
echo 8. Show 3-market logs
echo 9. Show latest 3-market input snapshot
echo 10. Show latest market-16 DB rows
echo 11. Plot latest market 16 (main+buy)
echo 12. Plot latest market 17 (main+buy)
echo 13. Plot latest market 18 (main+buy)
echo 14. Plot latest markets 16 17 18 separately (main+buy)
echo 15. Replot batches sequentially (main+buy)
echo 0. Exit
echo.
set /p choice=Select action:

if "%choice%"=="1" goto watch3
if "%choice%"=="2" goto watch16
if "%choice%"=="3" goto watch17
if "%choice%"=="4" goto watch18
if "%choice%"=="5" goto watch3test
if "%choice%"=="6" goto watch3push
if "%choice%"=="7" goto status3
if "%choice%"=="8" goto logs3
if "%choice%"=="9" goto snapshot3
if "%choice%"=="10" goto dbsnapshot3
if "%choice%"=="11" goto plot16
if "%choice%"=="12" goto plot17
if "%choice%"=="13" goto plot18
if "%choice%"=="14" goto plotall
if "%choice%"=="15" goto replotbatch
if "%choice%"=="0" goto end

echo.
echo Invalid choice.
pause
goto menu

:watch3
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_16__17__18.json when same-day file exists; rebuild when the file does not match requested markets.
echo Batch plot policy: write one main+buy PUSH batch PNG per market every 5 persisted rounds under output\sector_money_flow\TRADE_DATE\PUSH\.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 16 17 18 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --plot_every_rounds 5 --plot_metric_key BOTH --rounds 0 --continue_on_error true --output table
goto after_run

:watch16
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_16.json when same-day file exists; rebuild when the file does not match requested markets.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 16 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --rounds 0 --continue_on_error true --output table
goto after_run

:watch17
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_17.json when same-day file exists; rebuild when the file does not match requested markets.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 17 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --rounds 0 --continue_on_error true --output table
goto after_run

:watch18
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_18.json when same-day file exists; rebuild when the file does not match requested markets.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 18 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --rounds 0 --continue_on_error true --output table
goto after_run

:watch3test
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_16__17__18.json when same-day file exists; rebuild when the file does not match requested markets.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 16 17 18 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --rounds 2 --ignore_trading_window true --continue_on_error true --output table
goto after_run

:watch3push
echo.
echo Input snapshot policy: reuse output\sector_money_flow\TRADE_DATE\input_snapshot_16__17__18.json when same-day file exists; rebuild when the file does not match requested markets.
echo Batch plot policy: write one PUSH batch PNG per market every 2 persisted rounds under output\sector_money_flow\TRADE_DATE\PUSH\.
"%PYTHON_EXE%" scripts\sector_money_flow\watch.py --markets 16 17 18 --refresh_market AG --interval_seconds 60 --session_buffer_minutes 5 --top_n 10 --plot_every_rounds 2 --rounds 0 --continue_on_error true --output table
goto after_run

:status3
"%PYTHON_EXE%" scripts\sector_money_flow\status.py --markets 16 17 18 --refresh_market AG --output json
goto after_run

:logs3
"%PYTHON_EXE%" scripts\sector_money_flow\logs.py --markets 16 17 18 --refresh_market AG --limit 20 --output json
goto after_run

:snapshot3
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
set "SNAPSHOT_FILE=output\sector_money_flow\!LATEST_TRADE_DATE!\input_snapshot_16__17__18.json"
if not exist "!SNAPSHOT_FILE!" (
  echo.
  echo Input snapshot file not found:
  echo !SNAPSHOT_FILE!
  goto after_run
)
echo.
echo File: !SNAPSHOT_FILE!
type "!SNAPSHOT_FILE!"
goto after_run

:dbsnapshot3
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
"%PYTHON_EXE%" scripts\sector_money_flow\query_db.py --trade_date !LATEST_TRADE_DATE! --market 16 --limit 5 --output json
goto after_run

:plot16
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
echo.
echo Plot trade date: !LATEST_TRADE_DATE!
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 16 --metric_key BOTH --top_n 10 --output json
goto after_run

:plot17
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
echo.
echo Plot trade date: !LATEST_TRADE_DATE!
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 17 --metric_key BOTH --top_n 10 --output json
goto after_run

:plot18
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
echo.
echo Plot trade date: !LATEST_TRADE_DATE!
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 18 --metric_key BOTH --top_n 10 --output json
goto after_run

:plotall
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
echo.
echo Plot trade date: !LATEST_TRADE_DATE!
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 16 --metric_key BOTH --top_n 10 --output json
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 17 --metric_key BOTH --top_n 10 --output json
"%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --market 18 --metric_key BOTH --top_n 10 --output json
goto after_run

:replotbatch
call :resolve_latest_trade_date
if errorlevel 1 goto after_run
echo.
echo Replot trade date: !LATEST_TRADE_DATE!
set "BATCH_ROUND="
set /p BATCH_ROUND=Input start batch number, e.g. 2 for batch002:
if not defined BATCH_ROUND (
  echo Start batch number is required.
  goto after_run
)
echo !BATCH_ROUND!| findstr /r "^[1-9][0-9]*$" >nul
if errorlevel 1 (
  echo Start batch number must be a positive integer.
  goto after_run
)
set "ROUNDS_FILE=output\sector_money_flow\!LATEST_TRADE_DATE!\round_snapshots.jsonl"
if not exist "!ROUNDS_FILE!" (
  echo Batch snapshot file not found:
  echo !ROUNDS_FILE!
  goto after_run
)
for /f %%C in ('find /v /c "" ^< "!ROUNDS_FILE!"') do set "LAST_BATCH_ROUND=%%C"
if not defined LAST_BATCH_ROUND (
  echo Failed to resolve latest batch number from:
  echo !ROUNDS_FILE!
  goto after_run
)
if !BATCH_ROUND! GTR !LAST_BATCH_ROUND! (
  echo Start batch number !BATCH_ROUND! exceeds latest batch !LAST_BATCH_ROUND!.
  goto after_run
)
echo Replot metric: BOTH
echo Replot batch range: batch!BATCH_ROUND! to batch!LAST_BATCH_ROUND!
for /l %%N in (!BATCH_ROUND!,1,!LAST_BATCH_ROUND!) do (
  echo.
  echo [replot] batch%%N
  "%PYTHON_EXE%" scripts\sector_money_flow\plot.py --trade_date !LATEST_TRADE_DATE! --batch_round %%N --metric_key BOTH --output json
)
goto after_run

:after_run
echo.
pause
goto menu

:resolve_latest_trade_date
set "LATEST_TRADE_DATE="
for /f "delims=" %%D in ('dir /b /ad /o-n "output\sector_money_flow" 2^>nul') do (
  echo %%D| findstr /r "^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$" >nul
  if not errorlevel 1 (
    set "LATEST_TRADE_DATE=%%D"
    goto resolve_latest_trade_date_done
  )
)
:resolve_latest_trade_date_done
if not defined LATEST_TRADE_DATE (
  echo.
  echo No trade-date artifact directory found under output\sector_money_flow.
  exit /b 1
)
exit /b 0

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
