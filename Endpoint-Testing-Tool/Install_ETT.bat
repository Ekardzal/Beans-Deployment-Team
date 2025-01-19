@echo off
setlocal enabledelayedexpansion

:: Define the paths of the files and folders to check
set "projectFolder=Endpoint-Testing-Tool"
:: Define the destination directory
set "destination=%userprofile%\Desktop\"
if exist "%destination%" (goto PATH2)
set "destination=%userprofile%\OneDrive\Desktop\"
:PATH2
if not exist "%destination%\%projectFolder%" (mkdir "%destination%\%projectFolder%")
set "destination=%destination%%projectFolder%"
if not exist "%destination%" (echo [ERROR] Destination 1, 2 doesn't exist & goto ERRORPAUSE)
set "batchToStart=Beans-TT-Setup.bat"
set "appToStart=Test_Request_250118_17x41.py"
::BATCH 
set "file1=%projectFolder%\%batchToStart%"
::ALL OTHER FILES
set "file2=%projectFolder%\requirements.txt"
set "file3=%projectFolder%\%appToStart%"
::set "file4=C:\path\to\file4.txt"
::set "file5=C:\path\to\file5.txt"
::set "file6=C:\path\to\file6.txt"
::set "file7=C:\path\to\file7.txt"
::set "file8=C:\path\to\file8.txt"
set "folder1=%projectFolder%\templates"
set "folder2=%projectFolder%\static"
set "folder3=%projectFolder%\fonts"
::set "folder4=C:\path\to\folder4"
::set "folder5=C:\path\to\folder5"
::set "folder6=C:\path\to\folder6"
::set "folder7=C:\path\to\folder7"
::set "folder8=C:\path\to\folder8"

:: Initialize counters
set "found=0"
set "total=6"

if exist "%projectFolder%" (echo Project Main Folder exists & goto CHECK2) else (echo Project Main Folder is missing & goto END)
:CHECK2
:: Check if each file and folder exists
for %%F in ("%file1%" "%file2%" "%file3%" "%file4%" "%file5%" "%file6%" "%file7%" "%file8%" "%folder1%" "%folder2%" "%folder3%" "%folder4%" "%folder5%" "%folder6%" "%folder7%" "%folder8%") do (
    if exist "%%F" (
        set /a found+=1
        echo Found: %%F
    ) else (
        echo Not found: %%F
    )
)

:: Display the progress
echo Exist Check [%found%/%total%]
if "%found%" NEQ "%total%" (echo [ERROR] %found% There are missing files or folders & goto ERRORPAUSE)

:: Copy the found files to the destination
for %%F in ("%file1%" "%file2%" "%file3%" "%file4%" "%file5%" "%file6%" "%file7%" "%file8%") do (
    if exist "%%F" (
        echo Copying %%F to %destination%
        copy "%%F" "%destination%"
    )
)

:: Überprüfen, ob jeder Ordner existiert und Kopieren
for %%F in ("%folder1%" "%folder2%" "%folder3%") do (
    if exist "%%F" (
        set /a found+=1
        echo Found: %%F
        echo Copying folder %%F to %destination%
        xcopy "%%F" "%destination%\%%~nxF" /E /I /H /Y
    ) else (
        echo Not found: %%F
    )
)

pause >nul
If exist "%destination%\%batchToStart%" (echo SUCCESS& echo. & echo "%destination%\%batchToStart%" & start /d "%destination%\" %batchToStart%) else (echo ERROR & goto ERRORPAUSE)

:END
::pause >nul
:: End of script
endlocal

:ERRORPAUSE
pause >nul
endlocal
