@echo off
echo PostgreSQL Container Configuration
echo ===================================
echo Container: postgres-dev
echo User: devuser
echo Password: devpassword
echo Database: dev-app
echo Port: 5432
echo ===================================
python core.py postgres --name postgres-dev --user devuser --password devpassword --db dev-app --port 5432
pause
