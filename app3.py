
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# Protezione con password
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

# Caricamento o inizializzazione dati
if "dati_azienda" not in st.session_state:
    df_demo = pd.DataFrame({
        "anno": [2020, 2021, 2022],
        "ricavi": [100000, 120000, 140000],
        "costi": [80000, 90000, 95000],
    })
    df_demo["utile_netto"] = df_demo["ricavi"] - df_demo["costi"]
    df_demo["margine"] = (df_demo["utile_netto"] / df_demo["ricavi"]) * 100
    df_demo["crescita"] = [0] + [
        ((df_demo["utile_netto"].iloc[i] - df_demo["utile_netto"].iloc[i - 1]) / df_demo["utile_netto"].iloc[i - 1]) * 100
        for i in range(1, len(df_demo))
    ]
    st.session_state["dati_azienda"] = df_demo

df = st.session_state["dati_azienda"]

# Tabs principali
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF"])

with tab1:
    st.write("### ✏️ Inserisci o aggiungi dati")
    numero_anni = st.number_input("Quanti anni vuoi inserire?", min_value=1, max_value=20, step=1, value=3)
    new_data = []
    for i in range(numero_anni):
        st.markdown(f"**Anno {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            anno = st.number_input(f"Anno", min_value=1900, max_value=2100, key=f"anno_{i}")
            ricavi = st.number_input(f"Ricavi", min_value=0, key=f"ricavi_{i}")
        with col2:
            costi = st.number_input(f"Costi", min_value=0, key=f"costi_{i}")
            utile = ricavi - costi
        margine = (utile / ricavi * 100) if ricavi != 0 else 0
        new_data.append({"anno": anno, "ricavi": ricavi, "costi": costi, "utile_netto": utile, "margine": margine})

    if st.button("💾 Salva dati"):
        new_df = pd.DataFrame(new_data)
        combined = pd.concat([df, new_df], ignore_index=True).drop_duplicates(subset="anno").sort_values("anno")
        combined["crescita"] = [0] + [
            ((combined["utile_netto"].iloc[i] - combined["utile_netto"].iloc[i - 1]) / combined["utile_netto"].iloc[i - 1]) * 100
            if combined["utile_netto"].iloc[i - 1] != 0 else 0
            for i in range(1, len(combined))
        ]
        combined.reset_index(drop=True, inplace=True)
        st.session_state["dati_azienda"] = combined
        st.success("✅ Dati salvati!")

    st.write("### 📋 Dati attuali")
    st.dataframe(st.session_state["dati_azienda"])

with tab2:
    if not df.empty:
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
    if not df.empty:
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
    if not df.empty:
        st.write("### 📄 Download PDF")
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots()
            ax.axis("off")
            ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
            pdf.savefig(fig, bbox_inches="tight")
        buffer.seek(0)
        st.download_button("📥 Scarica PDF", buffer, "report_finanziario.pdf", "application/pdf")
