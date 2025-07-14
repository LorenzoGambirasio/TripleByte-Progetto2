@echo off
setlocal EnableDelayedExpansion

echo ==================================================
echo TripleByte Progetto2 - INSTALLER CORRETTO (Windows)
echo ==================================================
echo.

REM --- 1. VERIFICA REQUISITI DI SISTEMA ---
echo Verifico requisiti di sistema...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: Python non trovato! Installa Python 3.x e assicurati che sia nel PATH.
  pause
  exit /b 1
)

where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: psql non trovato! Installa PostgreSQL e assicurati che sia nel PATH.
  pause
  exit /b 1
)

where createdb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: createdb non trovato! Installa PostgreSQL e assicurati che sia nel PATH.
  pause
  exit /b 1
)

where dropdb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo ERRORE: dropdb non trovato! Installa PostgreSQL e assicurati che sia nel PATH.
  pause
  exit /b 1
)

echo Requisiti OK.
echo.

REM --- 2. CONTROLLO E LETTURA FILE .ENV ---
IF NOT EXIST ".env" (
  echo ERRORE: File .env mancante! Copia .env.example in .env e configuralo.
  pause
  exit /b 1
)


FOR /F "tokens=1,2 delims==" %%A IN (.env) DO set %%A=%%B

echo Credenziali DB caricate per l'utente: %DB_USER%
echo.

REM --- 3. CREAZIONE DATABASE (MODO ROBUSTO E AUTOMATICO) ---
echo Gestione Database: %DB_NAME%
echo.


echo  - Imposto la password per l'automazione...
set PGPASSWORD=%DB_PASSWORD%

echo  - Elimino il database precedente (se esiste)...
dropdb --if-exists -U %DB_USER% %DB_NAME%

echo  - Creo un nuovo database...
createdb -U %DB_USER% %DB_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: Impossibile creare il database %DB_NAME%. Controlla utente e password nel file .env.
    pause
    exit /b 1
)

echo  - Importo schema e dati...
psql -U %DB_USER% -d %DB_NAME% -f db_dump.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: Impossibile importare il file db_dump.sql.
    pause
    exit /b 1
)


set PGPASSWORD=

echo Database pronto.
echo.

REM --- 4. CONFIGURAZIONE AMBIENTE PYTHON E DIPENDENZE ---
echo Configuro ambiente virtuale Python...

REM Crea l'ambiente virtuale se non esiste
IF NOT EXIST "venv" (
    echo  - Creo l'ambiente virtuale 'venv'...
    python -m venv venv
)

REM Attiva l'ambiente virtuale
echo  - Attivo l'ambiente virtuale...
call "venv\Scripts\activate.bat"

echo  - Aggiorno pip...
python -m pip install --upgrade pip

echo  - Installo le dipendenze da requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: L'installazione delle dipendenze con pip e' fallita.
    pause
    exit /b 1
)
echo Dipendenze installate con successo.
echo.

REM --- 5. VERIFICA E AVVIO DJANGO ---
echo Verifico configurazione Django...
python manage.py check
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: Il check di Django e' fallito.
    pause
    exit /b 1
)
echo Configurazione Django OK.
echo.

echo Avvio server Django su http://127.0.0.1:8000 ...
echo (Premi CTRL+C per fermare il server)
echo.
python manage.py runserver

echo.
echo INSTALLAZIONE COMPLETATA!
pause
