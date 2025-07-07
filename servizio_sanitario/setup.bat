@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo TripleByte Progetto2 - INSTALLER (Windows)
echo ==========================================
echo.

REM Verifica requisiti di sistema
echo Verifico requisiti di sistema...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: Python non trovato! Installa Python 3.x.
  exit /b 1
)

where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: psql non trovato! Installa PostgreSQL.
  exit /b 1
)

where createdb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: createdb non trovato! Installa PostgreSQL.
  exit /b 1
)

echo Requisiti OK.
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


echo.
echo Controllo se le tabelle sono già popolate...

FOR /F \"tokens=*\" %%A IN ('psql -U %DB_USER% -d %DB_NAME% -t -c \"SELECT COUNT(*) FROM cittadini;\"') DO set COUNT=%%A

set COUNT=%COUNT: =%

IF %COUNT% GTR 0 (
  echo Dati già presenti, skip import schema.
) ELSE (
  echo Importo schema + dati reali...
  psql -U %DB_USER% -d %DB_NAME% -f db_dump.sql
)



echo.
echo Importo schema + dati reali...
psql -U %DB_USER% -d %DB_NAME% -f db_dump.sql

echo.
echo Installo dipendenze Python...
pip install -r requirements.txt

echo.
echo Verifico configurazione Django...
python manage.py check

echo.
echo Avvio server Django su http://127.0.0.1:8000 ...
python manage.py runserver 0.0.0.0:8000

echo.
echo INSTALLAZIONE COMPLETATA!
pause
