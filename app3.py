import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

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
st.title("\U0001f4ca Analisi Finanziaria - Serramenti Renato Orrù")

# Selezione tipo di periodo
periodo = st.sidebar.selectbox("Seleziona il periodo di analisi:", ["Annuale", "Mensile", "Settimanale", "Giornaliero"])

# Inizializzazione dati demo
if "dati_azienda" not in st.session_state:
    st.session_state["dati_azienda"] = pd.DataFrame()

df = st.session_state["dati_azienda"]

# Tabs
inserimento, dashboard, grafici, pdf = st.tabs(["\U0001f4e5 Inserimento", "\U0001f4ca Dashboard", "\U0001f4c8 Grafici", "\U0001f4c4 PDF"])

with inserimento:
    st.subheader(f"Inserimento dati ({periodo.lower()})")
    numero_righe = st.number_input("Quante righe vuoi inserire?", min_value=1, max_value=20, value=3)
    nuove_righe = []

    for i in range(numero_righe):
        with st.expander(f"Riga {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.text_input("Data (formato libero, es. 2024 o 2024-03)", key=f"data_{i}")
                ricavi = st.number_input("Ricavi", min_value=0.0, key=f"ricavi_{i}")
            with col2:
                costi = st.number_input("Costi", min_value=0.0, key=f"costi_{i}")
                utile = ricavi - costi
                margine = (utile / ricavi * 100) if ricavi else 0
            nuove_righe.append({"periodo": data, "ricavi": ricavi, "costi": costi, "utile_netto": utile, "margine": margine})

    if st.button("\U0001f4be Salva dati"):
        nuovo_df = pd.DataFrame(nuove_righe)
        combined = pd.concat([df, nuovo_df], ignore_index=True).drop_duplicates(subset="periodo").sort_values("periodo")
        combined["crescita"] = [0] + [
            ((combined["utile_netto"].iloc[i] - combined["utile_netto"].iloc[i - 1]) / combined["utile_netto"].iloc[i - 1]) * 100
            if combined["utile_netto"].iloc[i - 1] != 0 else 0
            for i in range(1, len(combined))
        ]
        st.session_state["dati_azienda"] = combined
        st.success("\u2705 Dati salvati!")

    st.dataframe(st.session_state["dati_azienda"])

with dashboard:
    if not df.empty:
        st.metric("\U0001f4c8 Media Utile Netto", f"\u20ac {df['utile_netto'].mean():,.2f}")
        st.metric("\U0001f4c9 Margine medio %", f"{df['margine'].mean():.2f} %")
        st.metric("\U0001f4ca Crescita media utile %", f"{df['crescita'].mean():.2f} %")

with grafici:
    if not df.empty:
        fig, ax = plt.subplots()
        index = range(len(df))
        ax.bar([i - 0.2 for i in index], df["ricavi"], width=0.2, label="Ricavi", color="blue")
        ax.bar(index, df["costi"], width=0.2, label="Costi", color="red")
        ax.bar([i + 0.2 for i in index], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
        ax.set_xticks(index)
        ax.set_xticklabels(df["periodo"].astype(str), rotation=45)
        ax.legend()
        st.pyplot(fig)

with pdf:
    if not df.empty:
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots()
            ax.axis("off")
            ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
            pdf.savefig(fig, bbox_inches="tight")
        buffer.seek(0)
        st.download_button("\U0001f4e5 Scarica PDF", buffer, "report_finanziario.pdf", "application/pdf")