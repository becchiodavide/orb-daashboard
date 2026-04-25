# ORB Dashboard Deploy

Cartella pulita per pubblicare la dashboard su Streamlit Cloud.

## File inclusi

- `dashboard.py`: app Streamlit.
- `config.py`: configurazione Google Sheet pubblico.
- `requirements.txt`: dipendenze per Streamlit Cloud.
- `.streamlit/config.toml`: tema e configurazione Streamlit.

## Prima del deploy

Assicurati che il Google Sheet configurato in `config.py` sia leggibile come:

`Chiunque abbia il link -> Visualizzatore`

La dashboard legge il foglio tramite URL CSV pubblico, quindi qui non servono chiavi API.

## Cosa non caricare

Non caricare mai:

- cartella `credentials/`
- file `.json` con chiavi
- CSV locali delle operazioni
- dataset Databento
- cache `.pkl`

## Streamlit Cloud

1. Carica questa cartella in un repository GitHub.
2. Crea una nuova app su Streamlit Cloud.
3. Main file path: `dashboard.py`.
4. Apri il link generato da telefono.
