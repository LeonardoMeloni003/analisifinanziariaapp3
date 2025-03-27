import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import os
import requests

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://fpblplgqvekuekorumkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwYmxwbGdxdmVrdWVrb3J1bWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NzY0MjAsImV4cCI6MjA1ODU1MjQyMH0.oPFXbOcbbhqOqkpOYyXJ2PLaXLyCwHdC-sWZ_186k0g"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}
PASSWORD = "analisi2024"

# --- LOGIN ---
def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Inserisci la password per accedere:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("❌ Password errata. Riprova:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- SFONDO BUSINESS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #1e3c72, #2a5298);
        background-attachment: fixed;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGO AZIENDALE ---
logo = Image.open("logo.jpg")
st.image(logo, width=120)
st.markdown("### **Serramenti Renato Orrù**")

# --- HOMEPAGE ---
st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")
st.markdown("""
Benvenuto nell'applicazione di **analisi finanziaria**.

🔹 **Azienda analizzata:** Serramenti Renato Orrù  
🔐 L’accesso è protetto da password condivisa.
""")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📥 Inserimento Dati", "📈 Grafici", "📄 Download PDF"])

with tab1:
    st.sidebar.header("Inserisci i dati")

    num_anni = st.sidebar.number_input("Numero di anni", min_value=1, max_value=10, value=4)
    anni = [st.sidebar.number_input(f"Anno {i + 1}", min_value=2000, max_value=2100, value=2020 + i) for i in range(num_anni)]
    ricavi = [st.sidebar.number_input(f"Ricavi Anno {anni[i]}", min_value=0, value=1000000) for i in range(num_anni)]
    costi = [st.sidebar.number_input(f"Costi Anno {anni[i]}", min_value=0, value=1000000) for i in range(num_anni)]

    utile_netto = [r - c for r, c in zip(ricavi, costi)]
    margine_profitto = [(u / r * 100) if r != 0 else 0 for u, r in zip(utile_netto, ricavi)]
    crescita_utile = [0] + [((utile_netto[i] - utile_netto[i - 1]) / utile_netto[i - 1] * 100) if utile_netto[i - 1] != 0 else 0 for i in range(1, len(utile_netto))]

    df = pd.DataFrame({
        "Anno": anni,
        "Ricavi": ricavi,
        "Costi": costi,
        "Utile Netto": utile_netto,
        "Margine di Profitto (%)": margine_profitto,
        "Crescita Utile Netto (%)": crescita_utile
    })

    st.session_state["dati_azienda"] = df

    # Salvataggio su Supabase
    for _, row in df.iterrows():
        dati = {
            "anno": int(row["Anno"]),
            "ricavi": float(row["Ricavi"]),
            "costi": float(row["Costi"]),
            "utile_netto": float(row["Utile Netto"]),
            "margine": float(row["Margine di Profitto (%)"]),
            "crescita": float(row["Crescita Utile Netto (%)"])
        }
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/dati%20finanziari?on_conflict=anno",
            headers=headers,
            json=dati
        )
        if response.status_code >= 400:
            st.warning(f"⚠️ Errore nel salvataggio dei dati: {response.status_code} - {response.text}")

    st.write("### 📋 Dati Inseriti e Indicatori")
    st.dataframe(df)

# (Il resto del codice rimane invariato per la visualizzazione dei grafici e PDF)
