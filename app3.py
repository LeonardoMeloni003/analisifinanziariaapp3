import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import requests

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://fpblplgqvekuekorumkr.supabase.co"
SUPABASE_KEY = "LA_TUA_CHIAVE_SUPABASE"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

PASSWORD = "analisi2024"

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

st.set_page_config(page_title="Analisi Finanziaria", layout="wide")

st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")

def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).sort_values("anno") if response.json() else pd.DataFrame()
    else:
        st.error("❌ Errore nel recupero dati")
        return pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF"])

if 'dati_azienda' not in st.session_state:
    st.session_state['dati_azienda'] = load_data()

df = st.session_state["dati_azienda"]

if df.empty:
    st.warning("Nessun dato presente.")
# --- DASHBOARD ---
with tab2:
    if not df.empty:
        st.write("### 📊 KPI Dashboard")
        media_utile = df['utile_netto'].mean()
        media_margine = df['margine'].mean()
        media_crescita = df['crescita'].mean()

        st.metric("📈 Media Utile Netto", f"€ {media_utile:,.2f}")
        st.metric("📉 Margine medio %", f"{media_margine:.2f} %")
        st.metric("📊 Crescita media utile %", f"{media_crescita:.2f} %")

        st.write("### 💬 Commento automatico sui dati")

        if media_margine > 25:
            st.success("🟢 Ottima redditività: il margine medio è superiore al 25%.")
        elif media_margine > 15:
            st.info("🟡 Margine positivo ma migliorabile.")
        else:
            st.warning("🔴 Margine basso: è consigliabile rivedere i costi.")

        if media_crescita > 10:
            st.success("📈 Utile netto in forte crescita negli ultimi anni.")
        elif media_crescita > 0:
            st.info("📊 Utile netto stabile o leggermente in crescita.")
        else:
            st.warning("📉 Utile netto in calo: serve attenzione alla gestione.")

# --- GRAFICI ---
with tab3:
    if not df.empty:
        st.write("### 📊 Grafico Ricavi, Costi, Utile")
        fig, ax = plt.subplots(figsize=(10, 4))
        x = range(len(df))
        ax.bar([i - 0.2 for i in x], df["ricavi"], width=0.2, label="Ricavi", color="blue")
        ax.bar(x, df["costi"], width=0.2, label="Costi", color="red")
        ax.bar([i + 0.2 for i in x], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
        ax.set_xticks(x)
        ax.set_xticklabels(df["anno"].astype(str))
        ax.legend()
        st.pyplot(fig)

# --- PDF DOWNLOAD ---
with tab4:
    if not df.empty:
        st.write("### 📄 Download PDF")
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots()
            ax.axis('off')
            table = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                loc='center',
                cellLoc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            pdf.savefig(fig, bbox_inches='tight')
        buffer.seek(0)
        st.download_button(
            label="📥 Scarica PDF",
            data=buffer,
            file_name="report_finanziario.pdf",
            mime="application/pdf"
        )
