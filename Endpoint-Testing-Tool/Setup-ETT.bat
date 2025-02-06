setlocal enabledelayedexpansion
@echo off
SET "EDITED=LAST TIME EDITED [30.01.25] - [22:34]"
:START
REM ADAPTABLE VARIABLES - CHANGE HERE !!!
:: Name der zu startenden App
set "appToStart=ETT.py"
:: Port zum Starten der WebApp
set "portWebApp=5000"
:: Name der virtuellen Umgebung
set venvDir=venv
:: Name der .txt datei die die nötigen Abhängigkeiten enthält
set "requirements_file=requirements.txt"
:: Definiere die Bibliotheken, die überprüft werden sollen
set "libs_to_check=flask requests pillow sqlitecloud dropbox"
:: Name dieser Batchdatei
set "batchName=Beans-TT-Setup.bat"
:: Muss stark angepasst werden bei Änderung, dient zum kopieren des lokalen Projekts in Git Repository
set /a "gitTest=0"
color 0a
REM CLS = Clear Screen
cls
REM Log File Variables
set timestamp=%date%%time%
set timestamp=%timestamp: =_%
set timestamp=%timestamp::=-%
set timestamp=%timestamp:~0,-6%
set /a checkInt=0
set "checkText="
REM Check for Files:
set /a "check1=0"
set "check1Text=python"
set /a "check2=0"
set "check2Text=pip"
set /a "check3=0"
set "check3Text=venv"
set /a "check4=0"
set "check4Text=%appToStart%"
set /a "check5=0"
set "check5Text=%requirements_file%"
REM Anzahl zu checkender Faktoren
set checkInt=0
set checkSum=5
:CHECKREQ
set /a "check1=0"
set /a "check2=0"
set /a "check3=0"
set /a "check4=0"
set /a "check5=0"
set /a "checkInt=0"
CLS
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
echo Check for script "%appToStart%"
if not exist %appToStart% (set /a check5=%check5%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
REM CHECK5
echo Check for requirements.txt...
if not exist %requirements_file% (set /a check5=%check5%+1 & color 0c) else (set /a checkInt=%checkInt%+1)
REM clear checking echos
CLS
title CD: %cd%
echo =======================================================================================
echo # %EDITED% # Timestamp: %timestamp% #
echo.
REM check requirements.txt
:: Zähler für gefundene Bibliotheken
set /a found_count=0
set /a total_count=0
set "foundReqList="
if exist %requirements_file% (
    :: Schleife zum Überprüfen der Bibliotheken
    for %%L in (%libs_to_check%) do (
        set /a total_count+=1
        REM echo Checking for %%L in %requirements_file%...
        findstr /i "%%L" %requirements_file% >nul
        if !errorlevel! neq 0 (
            set "foundReqList=!foundReqList![Missing]%%L "
            echo [Error] %%L is missing in %requirements_file%.
        ) else (
            set "foundReqList=!foundReqList![X]%%L "
            set /a found_count+=1
        )
    )
)
echo.
set "dependencies="
if %check1% GTR 0 (echo [Missing] %check1Text% & echo.) else (set "dependencies=!dependencies![X]%check1Text% ")
if %check2% GTR 0 (echo [Missing] %check2Text% & echo.) else (set "dependencies=!dependencies![X]%check2Text% ")
if %check3% GTR 0 (echo [Missing] %check3Text% & echo.) else (set "dependencies=!dependencies![X]%check3Text% ")
if %check4% GTR 0 (echo [Missing] %check4Text% & echo.) else (set "dependencies=!dependencies![X]%check4Text% ")
if %check5% GTR 0 (echo [Missing] %check5Text% & echo.) else (set "dependencies=!dependencies![X]%check5Text% ")
echo = [%checkInt%/%CheckSum%] !dependencies!
echo = [%found_count%/%total_count%] !foundReqList!
echo.
echo Hello %username% (^^_^^)
echo =======================================================================================
echo 			    MENU
echo =======================================================================================
:MENU
echo [1] Start App
echo.
echo [2] Start Virtual Environment
echo.
echo [3] Install Requirements
echo [4] Install Extras
echo .
set "input"=""
set /p input=:
if "%input: =%"=="" (goto START)                          
if "%input%"=="" (goto START) 
if "%input%"=="1" (goto STARTAPP)
if "%input%"=="2" (goto STARTVENV)
if "%input%"=="3" (goto CREATEVENV)
if "%input%"=="4" (goto INSTALLEXTRAS)
if "%input%"=="X" (goto CHECKREQ)
if "%input%"=="git" (goto COPYTOGIT)
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
if exist %requirements_file% (
    pip install --upgrade pip
    pip install -r %requirements_file%
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
:INSTALLEXTRAS
echo.
echo Are you sure, that you want to install flask-swagger-ui? [Yes = 1][No = 2]
set /p confirmExtraInstall=:
if "%confirmExtraInstall: =%"=="" (goto END)                          
if "%confirmExtraInstall%"=="" (goto END) 
if "%confirmExtraInstall%"=="1" (
	if exist "%cd%\venv" (
	cd /d "%cd%"
	call venv\Scripts\activate
	echo installing flask-swagger-ui...
	pip install flask-swagger-ui
	)
	if %errorlevel% neq 0 (
		echo.
		echo [Error] flask-swagger-ui installation failed
	) else (
		echo.
		echo flask-swagger-ui was installed successfully.
	)
)
if "%confirmExtraInstall%"=="2" (goto END)
pause >nul
goto END
:COPYTOGIT
::1 -> GIT HUB PATH
set "copyToPath=G:\Github Projects\Beans-Deployment-Team\Endpoint-Testing-Tool"
if not exist "%copyToPath%" (echo [ERROR] copyToPath="%copyToPath%" doesn't exist & pause >nul)
::
echo Do you want to copy the project to Github or your Desktop? [1 = G. / 2 = D.]
set "wannaCopy="
set /p wannaCopy=:
if "%wannaStart: =%"=="" (goto START)                          
if "%wannaCopy%"=="" (goto START) 
if "%wannaCopy%"=="1" (goto GIT)
if "%wannaCopy%"=="2" (goto COPYTODESK)
goto START
goto END
:COPYTODESK
set "copyToPath=%userprofile%\Desktop\Beans-ETT-Test"
if not exist "%copyToPath%" (mkdir "%copyToPath%")
:GIT
set /a "checkInt=0"
REM ----------------------------------
::2
set "copy1=requirements.txt"
if not exist "%copy1%" (echo [ERROR] copy1="%copy1%" doesn't exist & pause >nul)
::3
set "copy2=fonts"
if not exist "%copy2%" (echo [ERROR] copy2="%copy2%" doesn't exist & pause >nul)
::4
set "copy3=static"
if not exist "%copy3%" (echo [ERROR] copy1="%copy3%" doesn't exist & pause >nul)
::5
set "copy4=templates"
if not exist "%copy4%" (echo [ERROR] copy4="%copy4%" doesn't exist & pause >nul)
::6
set "copy5=%appToStart%"
if not exist "%copy5%" (echo [ERROR] copy5="%copy5%" doesn't exist & pause >nul)
REM ----------------------------------
set /a "checkSum=6"
if exist "%copyToPath%" (echo EXIST: "%copyToPath%" & set /a "checkInt=%checkInt%+1") 
if exist "%copy1%" (echo EXIST: "%copy1%" & set /a "checkInt=%checkInt%+1") 
if exist "%copy2%" (echo EXIST: "%copy2%" & set /a "checkInt=%checkInt%+1") 
if exist "%copy3%" (echo EXIST: "%copy3%" & set /a "checkInt=%checkInt%+1") 
if exist "%copy4%" (echo EXIST: "%copy4%" & set /a "checkInt=%checkInt%+1") 
if exist "%copy5%" (echo EXIST: "%copy5%" & set /a "checkInt=%checkInt%+1") 
echo [INFO] EXIST STATUS [%checkInt%/%checkSum%]
echo. 
echo Press any key to continue...
pause >nul
echo.
if %checkInt%==%checkSum% (
    echo everything exists copy process ist starting...
	echo.
    :: Kopiere alle Dateien und Ordner an das Ziel
    xcopy /Y "%copy1%" "%copyToPath%" >nul
	echo COPY "%copy1%" TO "%copyToPath%"
    ROBOCOPY /E "%copy2%" "%copyToPath%\%copy2%" >nul
	echo COPY "%copy2%" TO "%copyToPath%"
    ROBOCOPY /E "%copy3%" "%copyToPath%\%copy3%" >nul
	echo COPY "%copy3%" TO "%copyToPath%"
    ROBOCOPY /E "%copy4%" "%copyToPath%\%copy4%" >nul
	echo COPY "%copy4%" TO "%copyToPath%"
	xcopy /Y "%copy5%" "%copyToPath%" >nul
	echo COPY "%copy5%" TO "%copyToPath%"
    echo [SUCESS] copy process done!
) else (
    echo [Error] Files or Folders missing!
)
pause >nul
goto END
:END