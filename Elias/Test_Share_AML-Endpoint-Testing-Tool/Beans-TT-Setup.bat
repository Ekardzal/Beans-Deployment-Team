setlocal enabledelayedexpansion
@echo off
SET "EDITED=LAST TIME EDITED [11.01.24] - [16:21]"
:START
REM ADAPTABLE VARIABLES - CHANGE HERE !!!
:: Name of starting app
set "appToStart=Test_Request_251001_15x09.py"
:: Port for WebApp
set "portWebApp=5000"
:: Name der virtuellen Umgebung
set venvDir=venv
::Name of this batch file
set "batchName=Beans-TT-Setup.bat"
Color 0a
CLS
REM Check Width of Console Window
for /f "tokens=2 delims=:" %%a in ('mode con ^| find "Columns"') do set "width=%%a"
REM Remove Spaces
set "width=%width: =%"
REM Set Line
set "line="
for /l %%i in (1,1,%width%) do set "line=!line!-"
REM Log File Variables
set timestamp=%date%%time%
set timestamp=%timestamp: =_%
set timestamp=%timestamp::=-%
set timestamp=%timestamp:~0,-6%
set /a checkInt=0
set "checkText="
REM Check for Files:
set /a "check1=0"
set "check1Text=[Error] no python version found"
set /a "check2=0"
set "check2Text=[Error] no pip Version found"
set /a "check3=0"
set "check3Text=[Error] no venv folder found"
set /a "check4=0"
set "check4Text=[Error] no requirements.txt found"
REM Anzahl zu checkender Faktoren
set checkInt=0
set checkSum=4
:CHECKREQ
CLS
echo # %EDITED% # Timestamp: %timestamp% #
echo Current Path: %CD%
echo.
echo Check for python installation...
REM CHECK1
python --version >nul 2>&1
if %errorlevel% neq 0 (set /a check1=%check1%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
REM CHECK2
echo Check for pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (set /a check2=%check2%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
REM CHECK3
echo Check for venv folder...
if not exist venv (set /a check3=%check3%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
REM CHECK4
echo Check for requirements.txt...
if not exist requirements.txt (set /a check4=%check4%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
echo.
echo =========================================
echo 	REQUIREMENTS: [%checkInt%/%CheckSum%]
echo =========================================
if %check1% GTR 0 (echo %check1Text%)
if %check2% GTR 0 (echo %check2Text%)
if %check3% GTR 0 (echo %check3Text%)
if %check4% GTR 0 (echo %check4Text%)
echo.
echo =========================================
echo 	MENU
echo =========================================
:MENU
echo [1] Start App *name*
echo [2] Start Virtual Environment
echo [3] Install Requirements
echo [4] Check Requirements
echo .
set "input"=""
set /p input=:
if "%input: =%"=="" (goto START)                          
if "%input%"=="" (goto START) 
if "%input%"=="1" (goto STARTAPP)
if "%input%"=="2" (goto STARTVENV)
if "%input%"=="3" (goto CREATEVENV)
if "%input%"=="4" (goto CHECKREQ)
goto START
goto END
pause >nul
goto END
:STARTAPP
start http://127.0.0.1:%portWebApp%/
echo.
if exist "%cd%\venv" (
cd /d "%cd%"
REM start http://127.0.0.1:%portWebApp%/
start /b venv\Scripts\activate
"%cd%\venv\Scripts\python.exe" "%cd%\%appToStart%"
) else (echo Can't find "%cd%\venv")
REM if %errorlevel% equ 0 (start http://127.0.0.1:%portWebApp%/)
pause >nul
goto END
:STARTVENV
echo.
if exist "%cd%\venv" (
cd /d "%cd%"
start /b venv\Scripts\activate
) else (echo Can't find "%cd%\venv")
start http://127.0.0.1:%portWebApp%/
pause >nul
goto END
:CREATEVENV
echo.
echo installing python dependencies...
:: Prüfen, ob der venv-Ordner existiert
if not exist "%venvDir%" (
    echo creating virtual environment... 
    python -m venv %venvDir%
    if errorlevel 1 (
        echo [Error] during the creating process of the virtual environment!
        pause
        exit /b
    )
)
:: Aktivieren der virtuellen Umgebung
echo activating virtual environment...
call %venvDir%\Scripts\activate

:: Installieren von Abhängigkeiten
echo installing necessary dependencies...
if exist requirements.txt (
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo "requirements.txt" not found, please make sure it exists!
    pause
    exit /b
)
:: Abschlussmeldung
:SETUPDONE
echo.
echo Setup done! You can now start your project:
echo.
echo Do you want to start the app? [Yes = 1][No = 2]
set /p wannaStart=:
if "%wannaStart: =%"=="" (goto END)                          
if "%wannaStart%"=="" (goto END) 
if "%wannaStart%"=="1" (goto STARTAPP)
if "%wannaStart%"=="2" (goto END)
goto END
pause >nul
goto END
:END