# TripleByte-Progetto2

## Versione di sviluppo

# 🩺 Servizio Sanitario – Progetto Django con PostgreSQL

Sistema web per la gestione di cittadini, ospedali, patologie e ricoveri, realizzato con Django 5.2.1 e PostgreSQL.

---

## ⚙️ Requisiti

- Python 3.13+
- PostgreSQL 12 o superiore
- Ambiente virtuale (consigliato)
- `pip` aggiornato

---

## 🚀 Installazione del progetto

### 1. Clona il repository

```bash
git clone https://github.com/LorenzoGambirasio/TripleByte-Progetto2.git
cd servizio-sanitario
```

### 2. Crea e attiva un ambiente virtuale

```bash
python -m venv venv
venv\Scripts\activate          # Su Windows
# oppure
source venv/bin/activate       # Su macOS/Linux
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

---

## 🛠️ Configura PostgreSQL

### 4. Crea un database PostgreSQL

Apri il terminale ed esegui:

```bash
createdb servizio_sanitario
```

oppure da `pgAdmin`, crea un nuovo database chiamato `servizio_sanitario`.

### 5. Imposta le variabili d'ambiente

Copia il file di esempio:

```bash
cp .env.example .env
```

Modifica `.env` con le **tue credenziali PostgreSQL**:

```ini
DB_NAME=servizio_sanitario
DB_USER=postgres
DB_PASSWORD=la_tua_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🧱 Migrazioni del database

Se vuoi partire da zero (nuovo DB):

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🗃️ Ripristino da backup PostgreSQL (opzionale)

### Se ti è stato fornito un file `db_servizio.backup`:

```bash
pg_restore -U postgres -d servizio_sanitario db_servizio.backup
```

> 🔁 Sostituisci `postgres` con il tuo utente PostgreSQL se diverso

---

## ▶️ Avvio del server di sviluppo

```bash
python manage.py runserver
```

Accedi su `http://127.0.0.1:8000/`

---

## 📁 Struttura del progetto

```
servizio_sanitario/
├── main/                ← app Django principale
├── servizio_sanitario/  ← config Django (settings.py)
├── templates/           ← file HTML
├── static/              ← risorse statiche
├── db_servizio.backup   ← (opzionale) dump PostgreSQL
├── .env                 ← config locale NON DA COMMITTARE
├── .env.example         ← file di esempio da condividere
├── manage.py
└── requirements.txt
```

---

## 🤝 Collaborazione

1. Ognuno crea il proprio `.env` partendo da `.env.example`
2. Tutti usano PostgreSQL con stesso schema
3. Il backup `.backup` può essere condiviso per partire da dati comuni
4. Non committare `.env` nel repo (è in `.gitignore`)

---

## 🧪 Troubleshooting

### 🔴 Errore di autenticazione
```text
FATALE: autenticazione con password fallita per l'utente "postgres"
```
➡️ Soluzione: controlla `DB_USER` e `DB_PASSWORD` nel tuo `.env`.

### 🔴 `pg_restore` non trovato
➡️ Aggiungi PostgreSQL alla variabile di sistema PATH, oppure esegui da:
```bash
"C:\Program Files\PostgreSQL\<versione>\bin\pg_restore.exe"
```

---

## 📄 Licenza

Distribuito per scopi educativi.
