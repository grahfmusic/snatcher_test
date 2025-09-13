@echo off
REM Run Game Script (Windows CMD)
REM Launches the Snatchernauts framework using the RENPY_SDK environment variable.

setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM Default RENPY_SDK if not provided
if not defined RENPY_SDK set "RENPY_SDK=%USERPROFILE%\renpy-8.4.1-sdk"

set "RENPY_EXE=%RENPY_SDK%\renpy.exe"

REM Help
if "%~1"=="--help" goto :help

REM Parse args
set "DEBUG=0"
set "LINT=0"
set "COMPILE=0"

:parse_args
if "%~1"=="" goto :after_args
if "%~1"=="--debug"   (set "DEBUG=1"   & shift & goto :parse_args)
if "%~1"=="--lint"    (set "LINT=1"    & shift & goto :parse_args)
if "%~1"=="--compile" (set "COMPILE=1" & shift & goto :parse_args)
if "%~1"=="--help"    goto :help
echo Unknown option: %~1
exit /b 1

:help
echo Run Game Script - Snatchernauts Framework
echo.
echo Usage: scripts\run-game.cmd [--lint] [--debug] [--compile] [--help]
echo.
echo Options:
echo   --lint       Run lint check only (does not start game)
echo   --debug      Enable debug output when launching the game
echo   --compile    Force recompilation before launching the game
echo   --help       Show this help message
echo.
echo Environment Variables:
echo   RENPY_SDK    Path to Ren'Py SDK ^(default: %%USERPROFILE%%\renpy-8.4.1-sdk^)
echo                 Current: %%RENPY_SDK%%
if "%~1"=="--help" exit /b 0

:after_args

REM Validate SDK
if not exist "%RENPY_SDK%" (
  echo ERROR: RENPY_SDK directory not found: %RENPY_SDK%
  echo Set RENPY_SDK to your Ren'Py 8.4.x SDK directory.
  exit /b 1
)
if not exist "%RENPY_EXE%" (
  echo ERROR: renpy.exe not found in: %RENPY_SDK%
  echo Ensure you installed the Windows Ren'Py SDK and RENPY_SDK points to it.
  exit /b 1
)

echo Starting Snatchernauts Framework...
echo Using Ren'Py SDK: %RENPY_SDK%
echo Project directory: %CD%

if "%LINT%"=="1" (
  echo Running lint check...
  "%RENPY_EXE%" . lint
  if errorlevel 1 (
    REM Fallback to option-style if needed
    "%RENPY_EXE%" . --lint
    if errorlevel 1 exit /b %ERRORLEVEL%
  )
  echo Lint check completed.
  exit /b 0
)

if "%COMPILE%"=="1" (
  echo Compiling game...
  "%RENPY_EXE%" . --compile
  if errorlevel 1 (
    REM Fallback to subcommand
    "%RENPY_EXE%" . compile
    if errorlevel 1 exit /b %ERRORLEVEL%
  )
  echo Compilation completed.
)

if "%DEBUG%"=="1" (
  echo Debug mode enabled
  "%RENPY_EXE%" . --debug
) else (
  "%RENPY_EXE%" .
)

exit /b %ERRORLEVEL%

