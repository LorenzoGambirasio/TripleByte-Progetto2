#!/bin/bash

echo ""
echo "🚑 === TripleByte Progetto2 - INSTALLER ==="
echo ""

# ✅ Verifica requisiti di sistema
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

# ✅ Controllo file .env
if [ ! -f ".env" ]; then
  echo "⚠️  ERRORE: File .env mancante!"
  echo "👉 Copia .env.example e rinominalo in .env, poi riprova."
  exit 1
fi

# ✅ Carico variabili da .env
export $(grep -v '^#' .env | xargs)

echo "📌 Database: $DB_NAME"
echo "📌 Utente:   $DB_USER"
echo ""

# ✅ Verifica se DB esiste
DB_EXISTS=$(psql -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 && echo "yes" || echo "no")

if [ "$DB_EXISTS" = "no" ]; then
  echo "🔨 Creo database '$DB_NAME'..."
  createdb -U "$DB_USER" "$DB_NAME"
else
  echo "✅ Database già esistente: '$DB_NAME'"
fi


echo ""
echo "🔍 Controllo se le tabelle sono già popolate..."

# Verifica se la tabella 'cittadini' ha righe
ROW_COUNT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM cittadini;" | xargs)

if [ "$ROW_COUNT" -gt 0 ]; then
  echo "✅ Dati già presenti, skip import schema."
else
  echo "📂 Importo schema + dati reali..."
  psql -U "$DB_USER" -d "$DB_NAME" -f db_dump.sql
fi


echo ""
echo "📂 Importo schema + dati reali..."
psql -U "$DB_USER" -d "$DB_NAME" -f db_dump.sql

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
