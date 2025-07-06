#!/bin/bash
echo ">>> Creazione dell'ambiente virtuale 'venv'..."
python3 -m venv venv

echo ">>> Attivazione dell'ambiente virtuale..."
source venv/bin/activate

echo ">>> Installazione delle dipendenze..."
pip install -r requirements.txt

echo ">>> Creazione del file .env per il database..."
echo "DB_NAME=tuo_db_name" > .env
echo "DB_USER=tuo_db_user" >> .env
echo "DB_PASSWORD=tua_db_password" >> .env
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=5432" >> .env

echo ">>> IMPORTANTE: Verrà richiesta la password per l'utente PostgreSQL."
echo ">>> Importazione del database..."

psql -U tuo_db_user -d tuo_db_name -f ../backup_db/db_servizio_sanitario.sql

echo ">>> Avvio del server di sviluppo su http://127.0.0.1:8000/"
echo ">>> Per fermare il server, premere CTRL+C."
python manage.py runserver

deactivate