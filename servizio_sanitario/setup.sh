#!/bin/bash

echo ""
echo "🚑 === TripleByte Progetto2 - INSTALLER ==="
echo ""

# Verifica requisiti di sistema
echo "🔍 Verifico requisiti di sistema..."

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
  echo "❌ ERRORE: Python non trovato! Installa Python 3.x."
  exit 1
fi

if ! command -v psql &> /dev/null; then
  echo "❌ ERRORE: psql non trovato! Installa PostgreSQL."
  exit 1
fi

if ! command -v createdb &> /dev/null; then
  echo "❌ ERRORE: createdb non trovato! Installa PostgreSQL."
  exit 1
fi

echo "✅ Requisiti OK!"
echo ""

# Controllo file .env
if [ ! -f ".env" ]; then
  echo "⚠️  ERRORE: File .env mancante!"
  echo "👉 Copia .env.example e rinominalo in .env, poi riprova."
  exit 1
fi

# Carico variabili da .env
export $(grep -v '^#' .env | xargs)

echo "📌 Database: $DB_NAME"
echo "📌 Utente:   $DB_USER"
echo ""

# Verifica se DB esiste
DB_EXISTS=$(psql -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" | grep -q 1 && echo "yes" || echo "no")

if [ "$DB_EXISTS" = "no" ]; then
  echo "Creo database..."
  createdb -U "$DB_USER" "$DB_NAME"
  echo "Importo schema..."
  psql -U "$DB_USER" -d "$DB_NAME" -f db_dump.sql
else
  echo "DB già esistente."

  # Controllo se le tabelle sono popolate
  ROW_COUNT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM cittadini;" | xargs)
  if [ "$ROW_COUNT" -gt 0 ]; then
    echo "Tabelle già popolate, skip import."
  else
    echo "Importo schema..."
    psql -U "$DB_USER" -d "$DB_NAME" -f db_dump.sql
  fi
fi

echo ""
echo "📦 Installo dipendenze Python..."
pip install -r requirements.txt

echo ""
echo "🩺 Verifico configurazione Django..."
python3 manage.py check

echo ""
echo "🚀 Avvio server Django su http://127.0.0.1:8000 ..."
python3 manage.py runserver 0.0.0.0:8000

echo ""
echo "✅ INSTALLAZIONE COMPLETATA! Buon lavoro!"
