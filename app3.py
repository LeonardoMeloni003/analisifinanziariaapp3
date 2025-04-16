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
        st.text_input("🔒 Inserisci la password per accedere:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("❌ Password errata. Riprova:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()
st.set_page_config(page_title="Analisi Finanziaria", layout="wide")
st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")

# Caricamento dati da Supabase
def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.drop(columns=["data"], errors='ignore')
        df["anno"] = df["anno"].astype(int)
        return df.sort_values("anno") if not df.empty else pd.DataFrame()
    else:
        st.error("Errore nel recupero dati")
        return pd.DataFrame()

df = load_data()

# Modifica selezione anni con multiselect
anni_disponibili = sorted(df["anno"].unique().tolist())
anni_selezionati = st.sidebar.multiselect(
    "Seleziona gli anni da analizzare:", 
    options=anni_disponibili, 
    default=anni_disponibili
)

if anni_selezionati:
    df = df[df["anno"].isin(anni_selezionati)]

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF"])


with tab1:
    st.subheader("Inserimento Dati")

    with st.form("form_inserimento"):
        anno = st.number_input("Anno", min_value=2000, max_value=2100, step=1)
        ricavi = st.number_input("Ricavi (€)", min_value=0.0, step=1000.0)
        costi = st.number_input("Costi (€)", min_value=0.0, step=1000.0)

        utile = ricavi - costi
        margine = (utile / ricavi * 100) if ricavi else 0

        # Recupera l'anno precedente per calcolare la crescita
        anno_precedente = df[df["anno"] == anno - 1]
        if not anno_precedente.empty:
            utile_precedente = anno_precedente["utile_netto"].values[0]
            if utile_precedente != 0 and pd.notna(utile_precedente):
                crescita = ((utile - utile_precedente) / utile_precedente) * 100
            else:
                crescita = 0
        else:
            crescita = 0  # Nessuna crescita se non esiste l'anno precedente

        st.info(f"Utile Netto: € {utile:,.2f} | Margine: {margine:.2f} % | Crescita: {crescita:.2f} %")

        submitted = st.form_submit_button("💾 Salva dati")

        if submitted:
            if ricavi == 0:
                st.warning("⚠️ I ricavi devono essere maggiori di zero.")
            elif anno in df["anno"].values:
                st.warning(f"⚠️ L'anno {anno} è già presente nei dati.")
            else:
                nuova_riga = {
                    "anno": anno,
                    "ricavi": ricavi,
                    "costi": costi,
                    "utile_netto": utile,
                    "margine": margine,
                    "crescita": crescita
                }
                requests.post(f'{SUPABASE_URL}/rest/v1/dati_finanziari', headers=headers, json=nuova_riga)
                st.success("✅ Dati salvati con successo")
                st.rerun()

    st.write("### 📋 Dati attualmente salvati")
    st.dataframe(df)

    st.write("### 🔧 Modifica Dati Esistenti")
    for i, row in df.iterrows():
        with st.expander(f"Anno {row['anno']}"):
            nuovo_ricavi = st.number_input(f"Ricavi (€) - {row['anno']}", value=float(row['ricavi']), step=1000.0, key=f"mod_ricavi_{i}")
            nuovo_costi = st.number_input(f"Costi (€) - {row['anno']}", value=float(row['costi']), step=1000.0, key=f"mod_costi_{i}")

            nuovo_utile = nuovo_ricavi - nuovo_costi
            nuovo_margine = (nuovo_utile / nuovo_ricavi * 100) if nuovo_ricavi else 0
            st.info(f"Utile: €{nuovo_utile:,.2f} | Margine: {nuovo_margine:.2f}%")

            if st.button(f"💾 Salva Modifiche - {row['anno']}"):
                updated_row = {
                    "ricavi": nuovo_ricavi,
                    "costi": nuovo_costi,
                    "utile_netto": nuovo_utile,
                    "margine": nuovo_margine
                }
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/dati_finanziari?anno=eq.{row['anno']}",
                    headers=headers,
                    json=updated_row
                )
                st.success(f"Dati aggiornati per l'anno {row['anno']}")
                st.rerun()

with tab2:
    if not df.empty:
        df["crescita"] = [0] + [
            ((df["utile_netto"].iloc[i] - df["utile_netto"].iloc[i - 1]) / df["utile_netto"].iloc[i - 1]) * 100
            if df["utile_netto"].iloc[i - 1] != 0 and pd.notna(df["utile_netto"].iloc[i - 1])
            else 0
            for i in range(1, len(df))
        ]
        st.metric("📈 Media Utile Netto", f"€ {df['utile_netto'].mean():,.2f}")
        st.metric("📉 Margine medio %", f"{df['margine'].mean():.2f} %")
        st.metric("📊 Crescita media utile %", f"{df['crescita'].mean():.2f} %")

        st.write("### 💬 Commento automatico")
        if df["margine"].mean() > 20:
            st.success("🟢 Margine buono")
        elif df["margine"].mean() > 10:
            st.info("🟡 Margine nella media")
        else:
            st.warning("🔴 Margine basso")

with tab3:
    if not df.empty:
        st.write("### 📊 Grafico a Barre")
        fig_bar, ax = plt.subplots()
        index = range(len(df))
        ax.bar([i - 0.2 for i in index], df["ricavi"], width=0.2, label="Ricavi", color="blue")
        ax.bar(index, df["costi"], width=0.2, label="Costi", color="red")
        ax.bar([i + 0.2 for i in index], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
        ax.set_xticks(index)
        ax.set_xticklabels(df["anno"], rotation=45)
        ax.set_xlabel("Anno")
        ax.set_ylabel("Valori (€)")
        ax.legend()
        st.pyplot(fig_bar)

        st.write("### 📈 Andamento Utile Netto")
        fig_line, ax2 = plt.subplots()
        ax2.plot(df["anno"], df["utile_netto"], marker="o", color="green")
        ax2.set_xlabel("Anno")
        ax2.set_ylabel("Utile Netto (€)")
        ax2.set_title("Andamento Utile Netto")
        ax2.grid(True)
        st.pyplot(fig_line)

with tab4:
    if not df.empty:
        st.write("### 📄 Download PDF")
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
        st.download_button("📥 Scarica PDF", buffer, "report_analisi_finanziaria.pdf")