
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
        st.text_input(" Inserisci la password per accedere:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input(" Password errata. Riprova:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

st.set_page_config(page_title="Analisi Finanziaria", layout="wide")
st.title(" Analisi Finanziaria - Serramenti Renato Orr")

def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).sort_values("anno") if response.json() else pd.DataFrame()
    else:
        st.error(" Errore nel recupero dati")
        return pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs([" Inserimento", " Dashboard", " Grafici", " PDF"])

if 'dati_azienda' not in st.session_state:
    st.session_state['dati_azienda'] = load_data()

df = st.session_state["dati_azienda"]

with tab1:
    if not df.empty:
        st.write("###  Dati attuali")
        st.dataframe(df)

    st.write("###  Modifica o Inserisci Dati")
    anni = st.multiselect("Anni", list(range(2015, 2031)), default=df['anno'].tolist() if not df.empty else [])
    new_data = []
    for anno in anni:
        col1, col2 = st.columns(2)
        with col1:
            ricavi = st.number_input(f"Ricavi {anno}", min_value=0, key=f"ricavi_{anno}")
        with col2:
            costi = st.number_input(f"Costi {anno}", min_value=0, key=f"costi_{anno}")
        utile = ricavi - costi
        margine = (utile / ricavi * 100) if ricavi else 0
        new_data.append({"anno": anno, "ricavi": ricavi, "costi": costi, "utile_netto": utile, "margine": margine})

    if st.button(" Salva su Supabase"):
        requests.delete(f'{SUPABASE_URL}/rest/v1/dati_finanziari?anno=gt.0', headers=headers)
        for row in new_data:
            requests.post(f'{SUPABASE_URL}/rest/v1/dati_finanziari', headers=headers, json=row)
        st.success(" Dati salvati!")
        st.experimental_rerun()

with tab2:
    if not df.empty:
        media_utile = df['utile_netto'].mean()
        media_margine = df['margine'].mean()
        df["crescita"] = [0] + [((df["utile_netto"].iloc[i] - df["utile_netto"].iloc[i-1]) / df["utile_netto"].iloc[i-1]) * 100 for i in range(1, len(df))]
        media_crescita = df['crescita'].mean()

        st.metric(" Media Utile Netto", f" {media_utile:,.2f}")
        st.metric(" Margine medio %", f"{media_margine:.2f} %")
        st.metric(" Crescita media utile %", f"{media_crescita:.2f} %")

        st.write("###  Commento automatico")
        if media_margine > 25:
            st.success(" Ottima redditivit.")
        elif media_margine > 15:
            st.info(" Redditivit buona ma migliorabile.")
        else:
            st.warning(" Margine basso.")

        if media_crescita > 10:
            st.success(" Utile in forte crescita.")
        elif media_crescita > 0:
            st.info(" Utile stabile o in lieve crescita.")
        else:
            st.warning(" Utile in calo.")

with tab3:
    if not df.empty:
        st.write("###  Grafico")
        fig, ax = plt.subplots()
        index = range(len(df))
        ax.bar([i - 0.2 for i in index], df["ricavi"], width=0.2, label="Ricavi", color="blue")
        ax.bar(index, df["costi"], width=0.2, label="Costi", color="red")
        ax.bar([i + 0.2 for i in index], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
        ax.set_xticks(index)
        ax.set_xticklabels(df["anno"].astype(str))
        ax.legend()
        st.pyplot(fig)

with tab4:
    if not df.empty:
        st.write("###  Download PDF")
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots()
            ax.axis("off")
            ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
            pdf.savefig(fig, bbox_inches="tight")
        buffer.seek(0)
        st.download_button(" Scarica PDF", buffer, "report_finanziario.pdf", "application/pdf")