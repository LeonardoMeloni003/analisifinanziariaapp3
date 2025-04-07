
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# Protezione
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

# Caricamento o dati demo
if "dati_azienda" not in st.session_state:
    dati_demo = pd.DataFrame({
        "anno": [2020, 2021, 2022],
        "ricavi": [100000, 120000, 140000],
        "costi": [80000, 90000, 95000],
    })
    dati_demo["utile_netto"] = dati_demo["ricavi"] - dati_demo["costi"]
    dati_demo["margine"] = (dati_demo["utile_netto"] / dati_demo["ricavi"]) * 100
    dati_demo["crescita"] = [0] + [((dati_demo["utile_netto"].iloc[i] - dati_demo["utile_netto"].iloc[i-1]) / dati_demo["utile_netto"].iloc[i-1]) * 100 for i in range(1, len(dati_demo))]
    st.session_state["dati_azienda"] = dati_demo

df = st.session_state["dati_azienda"]

tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF"])

with tab1:
    st.write("### ✏️ Inserisci o modifica i dati")
    anni = st.multiselect("Anni", list(range(2015, 2031)))
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

    if st.button("💾 Salva localmente"):
        new_df = pd.DataFrame(new_data)
        if not new_df.empty:
            new_df["crescita"] = [0] + [((new_df["utile_netto"].iloc[i] - new_df["utile_netto"].iloc[i-1]) / new_df["utile_netto"].iloc[i-1]) * 100 for i in range(1, len(new_df))]
            st.session_state["dati_azienda"] = new_df
            st.success("✅ Dati salvati.")
            st.experimental_rerun()

    st.write("### 📋 Dati correnti")
    st.dataframe(df)

with tab2:
    if not df.empty:
        st.write("### 📊 Indicatori")
        st.metric("📈 Media Utile Netto", f"€ {df['utile_netto'].mean():,.2f}")
        st.metric("📉 Margine medio %", f"{df['margine'].mean():.2f} %")
        st.metric("📊 Crescita media utile %", f"{df['crescita'].mean():.2f} %")

        st.write("### 💬 Commento automatico")
        margine_medio = df["margine"].mean()
        crescita_media = df["crescita"].mean()

        if margine_medio > 25:
            st.success("🟢 Ottima redditività.")
        elif margine_medio > 15:
            st.info("🟡 Redditività buona ma migliorabile.")
        else:
            st.warning("🔴 Margine basso.")

        if crescita_media > 10:
            st.success("📈 Utile in forte crescita.")
        elif crescita_media > 0:
            st.info("📊 Utile stabile o in lieve crescita.")
        else:
            st.warning("📉 Utile in calo.")

with tab3:
    st.write("### 📊 Grafico Ricavi / Costi / Utile Netto")
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
    st.write("### 📄 Download PDF")
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots()
        ax.axis("off")
        ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
        pdf.savefig(fig, bbox_inches="tight")
    buffer.seek(0)
    st.download_button("📥 Scarica PDF", buffer, "report_finanziario.pdf", "application/pdf")
