@echo off
Set venv=.\venv

If Exist "%venv%\*.*" goto:activate
:setup
echo setup
py -m venv venv
call .\venv\Scripts\activate.bat
call pip install -r requirements.txt
echo @echo off > run.bat
echo call .\venv\Scripts\activate.bat >> run.bat
echo call python main.py >> run.bat
goto:end

If Not Exist "%venv%\*.*" goto:setup
:activate
If Not Exist "log.txt" goto:setup
echo activate
call .\venv\Scripts\activate.bat
goto:end

:end
call python main.py
