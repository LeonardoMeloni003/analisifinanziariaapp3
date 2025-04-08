import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import requests

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://fpblplgqvekuekorumkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwYmxwbGdxdmVrdWVrb3J1bWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NzY0MjAsImV4cCI6MjA1ODU1MjQyMH0.oPFXbOcbbhqOqkpOYyXJ2PLaXLyCwHdC-sWZ_186k0g"
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
        st.text_input("\U0001f512 Inserisci la password per accedere:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("\u274c Password errata. Riprova:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()
st.set_page_config(page_title="Analisi Finanziaria", layout="wide")
st.title("\U0001f4ca Analisi Finanziaria - Periodi Dinamici")

# Selezione tipo di periodo
tipo_periodo = st.sidebar.selectbox("Periodo di analisi:", ["Annuale", "Mensile", "Settimanale", "Giornaliero"])

# Caricamento dati da Supabase
def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    st.write("Status code:", response.status_code)
    st.write("Dettaglio:", response.text)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        return df.sort_values("periodo") if not df.empty else pd.DataFrame()
    else:
        st.error("Errore nel recupero dati")
        return pd.DataFrame()

df = load_data()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["\U0001f4e5 Inserimento", "\U0001f4ca Dashboard", "\U0001f4c8 Grafici", "\U0001f4c4 PDF"])

with tab1:
    st.subheader("Inserimento Dati")
    num_righe = st.number_input("Numero di periodi da inserire", min_value=1, max_value=20, value=3)
    nuove_righe = []

    for i in range(num_righe):
        st.markdown("---")
        st.markdown(f"### Periodo {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            periodo_val = st.text_input("Periodo (es. 2024, 2024-03, 2024-03-15)", key=f"periodo_{i}")
            ricavi = st.number_input("Ricavi", min_value=0.0, step=1000.0, key=f"ricavi_{i}")
        with col2:
            costi = st.number_input("Costi", min_value=0.0, step=1000.0, key=f"costi_{i}")
            utile = ricavi - costi
            margine = (utile / ricavi * 100) if ricavi else 0
        nuove_righe.append({
            "periodo": periodo_val,
            "ricavi": ricavi,
            "costi": costi,
            "utile_netto": utile,
            "margine": margine
        })

    if st.button("\U0001f4be Salva su Supabase"):
        requests.delete(f'{SUPABASE_URL}/rest/v1/finanza_periodi?periodo=gt.0', headers=headers)
        for riga in nuove_righe:
            requests.post(f'{SUPABASE_URL}/rest/v1/finanza_periodi', headers=headers, json=riga)
        st.success("\u2705 Dati salvati con successo")
        st.experimental_rerun()

    st.write("### \U0001f4cb Dati attualmente salvati")
    st.dataframe(df)

with tab2:
    if not df.empty:
        df["crescita"] = [0] + [((df["utile_netto"].iloc[i] - df["utile_netto"].iloc[i - 1]) / df["utile_netto"].iloc[i - 1]) * 100
                              if df["utile_netto"].iloc[i - 1] != 0 else 0
                              for i in range(1, len(df))]
        st.metric("\U0001f4c8 Media Utile Netto", f"\u20ac {df['utile_netto'].mean():,.2f}")
        st.metric("\U0001f4c9 Margine medio %", f"{df['margine'].mean():.2f} %")
        st.metric("\U0001f4ca Crescita media utile %", f"{df['crescita'].mean():.2f} %")

        st.write("### \U0001f4ac Commento automatico")
        if df["margine"].mean() > 20:
            st.success("\U0001f7e2 Margine buono")
        elif df["margine"].mean() > 10:
            st.info("\U0001f7e1 Margine nella media")
        else:
            st.warning("\U0001f534 Margine basso")

with tab3:
    if not df.empty:
        st.write("### \U0001f4ca Grafico a Barre")
        fig_bar, ax = plt.subplots()
        index = range(len(df))
        ax.bar([i - 0.2 for i in index], df["ricavi"], width=0.2, label="Ricavi", color="blue")
        ax.bar(index, df["costi"], width=0.2, label="Costi", color="red")
        ax.bar([i + 0.2 for i in index], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
        ax.set_xticks(index)
        ax.set_xticklabels(df["periodo"], rotation=45)
        ax.set_xlabel("Periodo")
        ax.set_ylabel("Valori (€)")
        ax.legend()
        st.pyplot(fig_bar)

        st.write("### \U0001f4c8 Andamento Utile Netto")
        fig_line, ax2 = plt.subplots()
        ax2.plot(df["periodo"], df["utile_netto"], marker="o", color="green")
        ax2.set_xlabel("Periodo")
        ax2.set_ylabel("Utile Netto (€)")
        ax2.set_title("Andamento Utile Netto")
        ax2.grid(True)
        st.pyplot(fig_line)

with tab4:
    if not df.empty:
        st.write("### \U0001f4c4 Download PDF")
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots()
            ax.axis("off")
            table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            pdf.savefig(fig, bbox_inches="tight")
        buffer.seek(0)
        st.download_button("\U0001f4e5 Scarica PDF", buffer, "report_analisi_finanziaria.pdf", "application/pdf")
