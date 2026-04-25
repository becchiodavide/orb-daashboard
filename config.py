"""Config centralizzata per dashboard e sync script.

Valori letti da variabili d'ambiente quando disponibili (utile per Streamlit Cloud),
altrimenti usa i default definiti qui (utile in locale).
"""
from __future__ import annotations

import os
from pathlib import Path

# --- Paths locali -----------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
CSV_PATH = PROJECT_ROOT / "Risultati operazioni" / "orb_trades.csv"
CREDS_PATH = PROJECT_ROOT / "credentials" / "gsheets_credentials.json"

# --- Google Sheets ----------------------------------------------------------
# ID del Google Sheet (pezzo URL fra /d/ e /edit)
SHEET_ID = os.getenv(
    "ORB_SHEET_ID",
    "1jctyoBh1IWK9CkUsqhuKuC6njnTH9Ckho4w0icgfH9I",
)
# Nome del tab (worksheet) dentro il Sheet. Lo script lo crea se manca.
SHEET_TAB = os.getenv("ORB_SHEET_TAB", "Trades")

# URL pubblico in formato CSV — usato dalla dashboard per leggere senza auth
# (richiede che il Sheet sia condiviso come "Anyone with the link — Viewer").
SHEET_PUBLIC_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq"
    f"?tqx=out:csv&sheet={SHEET_TAB}"
)
