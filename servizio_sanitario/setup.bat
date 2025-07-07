@echo off
echo.
echo === TripleByte Progetto2 - INSTALLER (Windows) ===
echo.

REM Controlla se .env esiste
IF NOT EXIST ".env" (
  echo  ERRORE: File .env mancante! Copia .env.example in .env
  exit /b
)

REM Leggi .env (approccio semplificato)
FOR /F "tokens=1,2 delims==" %%A IN (.env) DO set %%A=%%B

echo  DB: %DB_NAME%
echo  User: %DB_USER%

REM Crea DB se non esiste
psql -U %DB_USER% -tc "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" | findstr /C:"1" >nul
IF ERRORLEVEL 1 (
  echo  Creo DB...
  createdb -U %DB_USER% %DB_NAME%
) ELSE (
  echo  DB già esistente.
)

echo  Importo schema + dati...
psql -U %DB_USER% -d %DB_NAME% -f db_dump.sql

echo  Installo dipendenze Python...
pip install -r requirements.txt

echo  Verifico Django...
python manage.py check

echo  Avvio server...
python manage.py runserver 0.0.0.0:8000
