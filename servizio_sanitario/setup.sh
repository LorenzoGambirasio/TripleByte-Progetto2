#!/bin/bash

echo ""
echo "🚑 === TripleByte Progetto2 - INSTALLER ==="
echo ""

# ✅ Controllo file .env
if [ ! -f ".env" ]; then
  echo "⚠️  ERRORE: File .env mancante!"
  echo "👉 Copia .env.example e rinominalo in .env, poi riprova."
  exit 1
fi

# ✅ Carico variabili da .env
export $(grep -v '^#' .env | xargs)

# ✅ Parametri
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
echo "📂 Importo schema + dati reali..."
psql -U "$DB_USER" -d "$DB_NAME" -f db_dump.sql

echo ""
echo "📦 Installo dipendenze Python..."
pip install -r requirements.txt

echo ""
echo "🩺 Verifico configurazione Django..."
python manage.py check

echo ""
echo "🚀 Avvio server Django su http://127.0.0.1:8000 ..."
python manage.py runserver 0.0.0.0:8000

echo ""
echo "✅ INSTALLAZIONE COMPLETATA! Buon lavoro!"
