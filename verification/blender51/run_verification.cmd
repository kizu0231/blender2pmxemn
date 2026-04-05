@echo off
setlocal

if "%~1"=="" (
    echo Missing BlenderPath
    echo Usage: run_verification.cmd ^<BlenderPath^> [ScriptName]
    exit /b 1
)

set "BLENDER_PATH=%~1"
set "SCRIPT_NAME=%~2"

if "%SCRIPT_NAME%"=="" set "SCRIPT_NAME=check_issue13_coverage.py"

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "FOR_LOCAL_DIR=%REPO_ROOT%\forLocal"
set "BLENDER_USER_SCRIPTS=%FOR_LOCAL_DIR%\blender-user-scripts"
set "PYTHON_SCRIPT=%SCRIPT_DIR%%SCRIPT_NAME%"

if not exist "%BLENDER_PATH%" (
    echo Blender not found: %BLENDER_PATH%
    exit /b 1
)

if not exist "%PYTHON_SCRIPT%" (
    echo Script not found: %PYTHON_SCRIPT%
    exit /b 1
)

echo BLENDER_USER_SCRIPTS=%BLENDER_USER_SCRIPTS%
echo blender.exe=%BLENDER_PATH%
echo script=%PYTHON_SCRIPT%

"%BLENDER_PATH%" --background --factory-startup --python "%PYTHON_SCRIPT%"
exit /b %ERRORLEVEL%
