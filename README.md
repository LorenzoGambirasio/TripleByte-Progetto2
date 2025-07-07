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

## 🧾 Contesto e Obiettivi del Progetto

Questo progetto nasce nell'ambito della modellazione e implementazione di una **base di dati regionale** destinata alla **gestione informatizzata dei ricoveri ospedalieri**.

La Regione ha già a disposizione informazioni anagrafiche sui cittadini, identificati tramite il **Codice del Servizio Sanitario Nazionale (CSSN)**. Ogni cittadino è caratterizzato da dati personali quali nome, cognome, data e luogo di nascita, e indirizzo di residenza.

Anche gli **ospedali** sono registrati preventivamente: ciascuno identificato da un codice univoco, e descritto attraverso nome, città, indirizzo e **nome del Direttore Sanitario**. Una **persona può essere Direttore Sanitario di un solo ospedale**.

I **ricoveri** rappresentano il fulcro del sistema. Ogni ricovero è associato a:
- un ospedale,
- un cittadino (paziente),
- una data di inizio,
- una durata,
- un motivo,
- un costo,
- un codice univoco (relativamente all’ospedale).

Durante un ricovero, un paziente può essere curato per **una o più patologie**, ciascuna nota alla Regione. Ogni **patologia** è identificata da un codice, ed è associata a un nome e a un livello di **criticità** (es. da 1 a 10).  
Il sistema distingue due **sottoinsiemi** di patologie:
- **Patologie croniche**
- **Patologie mortali**  
Questi sottoinsiemi **non sono disgiunti né esaustivi**: una patologia può appartenere ad entrambi o a nessuno dei due.

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

**Linux/macOS:**
```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
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
