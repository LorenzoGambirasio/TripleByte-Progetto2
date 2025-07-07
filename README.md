# TripleByte – Servizio Sanitario 📊🩺

![Last Commit](https://img.shields.io/github/last-commit/LorenzoGambirasio/TripleByte-Progetto2?style=for-the-badge)
![Languages Count](https://img.shields.io/github/languages/count/LorenzoGambirasio/TripleByte-Progetto2?style=for-the-badge)

---

## 📌 Descrizione

**TripleByte – Servizio Sanitario** è un progetto universitario di *Programmazione Web* basato su **Django** con **PostgreSQL**, pensato per la gestione informatizzata dei ricoveri ospedalieri in ambito regionale.

---

## 🛠️ Tecnologie Utilizzate

![Markdown](https://img.shields.io/badge/Markdown-000?logo=markdown&logoColor=white&style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black&style=for-the-badge)
![HTML](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white&style=for-the-badge)
![CSS](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white&style=for-the-badge)
![AJAX](https://img.shields.io/badge/AJAX-000000?logo=javascript&logoColor=white&style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge)
![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white&style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge)
![SQL](https://img.shields.io/badge/SQL-4479A1?logo=mysql&logoColor=white&style=for-the-badge)

---

## 🧾 Contesto e Obiettivi

Il sistema modella una **base di dati regionale** per:

* **Cittadini:** identificati tramite **CSSN**, con dati anagrafici completi.
* **Ospedali:** identificati da codice univoco, con informazioni su nome, città, indirizzo e Direttore Sanitario.
* **Ricoveri:** associati a ospedale e cittadino, con motivazione, durata, costo, patologie curate.
* **Patologie:** con livello di criticità e sottoinsiemi *croniche* e *mortali*.

---

## ✨ Funzionalità Principali

* 🌐 Interfaccia responsive e intuitiva
* 📋 Gestione completa di ricoveri, cittadini, ospedali, patologie
* 🗂️ Importazione schema con **chiavi composite** e dati reali già pronti

---

## ⚙️ Requisiti di Sistema

✅ **Python 3.x** installato  
✅ **PostgreSQL** installato e attivo (porta predefinita: `5432`)  
✅ Utente PostgreSQL con permessi di creazione database (es. `postgres`)  
✅ `psql` e `createdb` inclusi nel `PATH` di sistema

---

## 📦 Contenuto del Repository

```
TripleByte-Progetto2/
│
├── setup.sh         # Script per Linux/macOS
├── setup.bat        # Script per Windows
├── .env.example     # Configurazione di esempio
├── db_dump.sql      # Dump SQL: schema + dati reali
├── requirements.txt # Librerie Python necessarie
├── manage.py        # Progetto Django
├── [cartella progetto]
├── [app principale]
```

---

## 🚀 Installazione e Avvio

### 1️⃣ Clona il repository

```bash
git clone https://github.com/LorenzoGambirasio/TripleByte-Progetto2.git
cd TripleByte-Progetto2/servizio_sanitario
```

### 2️⃣ Crea e configura `.env`

Copia l’esempio:

```bash
cp .env.example .env
```

Apri `.env` con un editor e inserisci **i tuoi parametri personali** per la connessione al database:

```
DB_NAME=TUO_NOME_DATABASE (es. servizio_sanitario)
DB_USER=TUO_USERNAME (es. postgres)
DB_PASSWORD=LA_TUA_PASSWORD (es. admin)
DB_HOST=localhost
DB_PORT=5432
```

---

### 3️⃣ Esegui l’installer

**Linux/macOS:**

```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**

Esegui `setup.bat` con doppio clic oppure da prompt:

```bat
setup.bat
```

---

## 🔍 Cosa fa lo `setup.sh`/`setup.bat`

* Verifica l’esistenza del database
* Se non esiste, lo crea (`createdb`)
* Importa **schema e dati reali** (`psql`)
* Installa le dipendenze Python (`requirements.txt`)
* Esegue un check del progetto Django
* Avvia il server su [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 👤 Autori

**Lorenzo Umberto Gambirasio – \[1087441]**
📧 [lorenzo.gambirasio@studenti.unibg.it](mailto:lorenzo.gambirasio@studenti.unibg.it)
🌐 [GitHub – @LorenzoGambirasio](https://github.com/LorenzoGambirasio)

**Alessandro Biscaro – \[1087892]**
📧 [a.biscaro@studenti.unibg.it](mailto:a.biscaro@studenti.unibg.it)
🌐 [GitHub – @AlessandroBiscaro](https://github.com/AlessandroBiscaro)

**Marco Valceschini – \[1086356]**
📧 [m.valceschini1@studenti.unibg.it](mailto:m.valceschini1@studenti.unibg.it)
🌐 [GitHub – @MarcoValceschini](https://github.com/MarcoValceschini)

---

## 📄 Licenza

Distribuito per **scopi educativi**.
