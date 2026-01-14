@echo off
echo [%date% %time%] Début de l'envoi des emails... >> "c:\Users\LENOVO\Desktop\PROJET\Sourcing\emails.log"
call "c:\Users\LENOVO\Desktop\PROJET\Sourcing\env\Scripts\activate.bat"
cd /d "c:\Users\LENOVO\Desktop\PROJET\Sourcing"
python manage.py send_pending_emails --max-emails=50 >> "c:\Users\LENOVO\Desktop\PROJET\Sourcing\emails.log" 2>&1
echo [%date% %time%] Fin de l'envoi des emails. >> "c:\Users\LENOVO\Desktop\PROJET\Sourcing\emails.log"
