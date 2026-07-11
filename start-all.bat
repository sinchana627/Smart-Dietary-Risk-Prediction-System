@echo off
cd /d "%~dp0\ml-api"
start cmd /k "python app.py"
cd /d "%~dp0\server"
start cmd /k "npm run dev"
cd /d "%~dp0\client"
start cmd /k "npm start"
echo Started ML API, backend, and client in separate command windows.
echo Use the browser at http://localhost:3000
