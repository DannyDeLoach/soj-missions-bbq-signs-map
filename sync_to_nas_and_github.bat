@echo off
echo.
echo ==========================================
echo   Deploying to Synology NAS (Instant)
echo ==========================================
echo Copying map files...
xcopy /y /q "index.html" "\\192.168.86.153\web\soj-missions-bbq-signs\"
xcopy /y /q "Missions BBQ Signs - Base map - Signs.txt" "\\192.168.86.153\web\soj-missions-bbq-signs\"
xcopy /y /q "Missions BBQ Signs - Base map- Groups.csv" "\\192.168.86.153\web\soj-missions-bbq-signs\"
xcopy /y /q "Missions BBQ Signs - Base map- SOJ.txt" "\\192.168.86.153\web\soj-missions-bbq-signs\"
echo NAS Deployment Complete!
echo Live at: http://192.168.86.153/soj-missions-bbq-signs/index.html
echo.
echo ==========================================
echo   Syncing to GitHub (Backup/Remote)
echo ==========================================
git add .
git commit -m "Update map files and sync to NAS"
git push origin main --force
echo.
echo -----------------------------------
echo SYNC COMPLETE!
echo -----------------------------------
pause
