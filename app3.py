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

# --- CARICAMENTO DATI DA SUPABASE ALL'AVVIO ---
if "dati_azienda" not in st.session_state:
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/dati%20finanziari?select=*",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df = df.sort_values("anno")
                df = df.rename(columns={
                    "anno": "Anno",
                    "ricavi": "Ricavi",
                    "costi": "Costi",
                    "utile_netto": "Utile Netto",
                    "margine": "Margine di Profitto (%)",
                    "crescita": "Crescita Utile Netto (%)"
                })
                st.session_state["dati_azienda"] = df

# 🔄 Ricarica i dati aggiornati da Supabase
try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/dati%20finanziari?select=*", headers=headers)
    if response.status_code == 200:
        dati = response.json()
        if dati:
            df = pd.DataFrame(dati).sort_values("anno")
            st.session_state["dati_azienda"] = df
except Exception as e:
    st.warning(f"⚠️ Impossibile aggiornare i dati da Supabase: {e}")
    except Exception as e:
        st.warning(f"⚠️ Errore nel caricamento dei dati da Supabase: {e}")

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

    for _, row in df.iterrows():
        dati = {
            "anno": int(row["Anno"]),
            "ricavi": float(row["Ricavi"]),
            "costi": float(row["Costi"]),
            "utile_netto": float(row["Utile Netto"]),
            "margine": float(row["Margine di Profitto (%)"]),
            "crescita": float(row["Crescita Utile Netto (%)"])
        }

        # PATCH con filtro su anno per aggiornare o creare se non esiste
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/dati%20finanziari?anno=eq.{dati['anno']}",
            headers=headers,
            json=dati
        )
        if response.status_code >= 400:
            st.warning(f"⚠️ Errore nel salvataggio dei dati: {response.status_code} - {response.text}")
        else:
            st.success(f"✅ Dati salvati per l'anno {dati['anno']}")
            st.code(response.text or "⚠️ Nessuna risposta ricevuta da Supabase")

    st.write("### 📋 Dati Inseriti e Indicatori")
    st.dataframe(df)

with tab2:
    if "dati_azienda" in st.session_state:
        df = st.session_state["dati_azienda"]
        anni = df["Anno"].tolist()
        ricavi = df["Ricavi"].tolist()
        costi = df["Costi"].tolist()
        utile_netto = df["Utile Netto"].tolist()

        st.write("### 📊 Confronto Ricavi, Costi e Utile Netto")
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.suptitle("Serramenti Renato Orrù", fontsize=14)
        bar_width = 0.3
        index = range(len(anni))

        ax.bar([i - bar_width for i in index], ricavi, width=bar_width, color='blue', label='Ricavi')
        ax.bar(index, costi, width=bar_width, color='red', label='Costi')
        ax.bar([i + bar_width for i in index], utile_netto, width=bar_width, color='green', label='Utile Netto')

        ax.set_xticks(index)
        ax.set_xticklabels(anni)
        ax.set_xlabel("Anno")
        ax.set_ylabel("Valore (€)")
        ax.set_title("Andamento Ricavi, Costi e Utile Netto")
        ax.legend()
        ax.grid(axis='y')

        st.pyplot(fig)

        st.write("### 📈 Andamento Utile Netto")
        fig_line, ax_line = plt.subplots(figsize=(10, 4))
        fig_line.suptitle("Serramenti Renato Orrù", fontsize=14)
        ax_line.plot(anni, utile_netto, marker="o", linestyle='-', color="green", linewidth=2)
        ax_line.set_title("Andamento dell'Utile Netto")
        ax_line.set_xlabel("Anno")
        ax_line.set_ylabel("Utile Netto (€)")
        ax_line.grid(True)

        st.pyplot(fig_line)

with tab3:
    if "dati_azienda" in st.session_state:
        df = st.session_state["dati_azienda"]

        st.write("### 📄 Scarica i report in PDF")

        grafici_buffer = BytesIO()
        with PdfPages(grafici_buffer) as pdf:
            pdf.savefig(fig)
            pdf.savefig(fig_line)
        grafici_pdf = grafici_buffer.getvalue()

        st.download_button(
            label="📥 Scarica PDF Grafici",
            data=grafici_pdf,
            file_name="grafici_analisi_finanziaria.pdf",
            mime="application/pdf"
        )

        dati_buffer = BytesIO()
        with PdfPages(dati_buffer) as pdf:
            fig_table, ax_table = plt.subplots(figsize=(12, 3))
            ax_table.axis('off')
            table = ax_table.table(
                cellText=df.values,
                colLabels=df.columns,
                cellLoc='center',
                loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            pdf.savefig(fig_table, bbox_inches='tight')
        dati_pdf = dati_buffer.getvalue()

        st.download_button(
            label="📥 Scarica PDF Tabella",
            data=dati_pdf,
            file_name="tabella_analisi_finanziaria.pdf",
            mime="application/pdf"
        )
