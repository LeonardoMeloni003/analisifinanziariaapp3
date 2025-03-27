import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import requests
from fpdf import FPDF

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://fpblplgqvekuekorumkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwYmxwbGdxdmVrdWVrb3J1bWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NzY0MjAsImV4cCI6MjA1ODU1MjQyMH0.oPFXbOcbbhqOqkpOYyXJ2PLaXLyCwHdC-sWZ_186k0g"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
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
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #1e3c72, #2a5298);
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# --- CARICAMENTO DATI DA SUPABASE ---
def load_data():
    response = requests.get(f"{SUPABASE_URL}/rest/v1/dati%20finanziari?select=*", headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).sort_values("anno") if response.json() else pd.DataFrame()
    else:
        st.error("❌ Errore nel recupero dei dati da Supabase")
        return pd.DataFrame()

df = load_data()
st.session_state["dati_azienda"] = df

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

    df_input = pd.DataFrame({
        "anno": anni,
        "ricavi": ricavi,
        "costi": costi,
        "utile_netto": utile_netto,
        "margine": margine_profitto,
        "crescita": crescita_utile
    })

    if st.button("Salva Dati"):
        for _, dati in df_input.iterrows():
            requests.post(f"{SUPABASE_URL}/rest/v1/dati%20finanziari", headers=headers, json=dati.to_dict())
        st.session_state["dati_azienda"] = load_data()
        st.success("✅ Dati salvati correttamente!")

    st.write("### 📋 Dati Inseriti e Indicatori")
    st.dataframe(df_input)

with tab2:
    if not df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        bar_width = 0.3
        index = range(len(df["anno"]))

        ax.bar([i - bar_width for i in index], df["ricavi"], width=bar_width, label='Ricavi', color='blue')
        ax.bar(index, df["costi"], width=bar_width, label='Costi', color='red')
        ax.bar([i + bar_width for i in index], df["utile_netto"], width=bar_width, label='Utile Netto', color='green')

        ax.set_xticks(index)
        ax.set_xticklabels(df["anno"])
        ax.legend()
        st.pyplot(fig)

with tab3:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
    pdf_output = pdf.output(dest='S').encode('latin1')
    st.download_button("📥 Scarica PDF Dati", pdf_output, "report_dati.pdf", "application/pdf")
