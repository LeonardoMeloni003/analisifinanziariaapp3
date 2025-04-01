import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
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

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #1e3c72, #2a5298);
    background-attachment: fixed;
}
</style>
""", unsafe_allow_html=True)

logo = Image.open("logo.jpg")
st.image(logo, width=120)
st.markdown("### **Serramenti Renato Orrù**")

st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")
st.markdown("""
Benvenuto nell'applicazione di **analisi finanziaria**.

🔹 **Azienda analizzata:** Serramenti Renato Orrù  
🔐 L’accesso è protetto da password condivisa.
""")

def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).sort_values("anno") if response.json() else pd.DataFrame()
    else:
        st.error(f"❌ Errore nel recupero dati: {response.text}")
        return pd.DataFrame()

# --- TABS PRINCIPALI ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento Dati", "📊 Dashboard", "📈 Grafici", "📄 Download PDF"])

with tab1:
    st.sidebar.header("Inserisci i dati")

    if 'dati_azienda' not in st.session_state:
        st.session_state["dati_azienda"] = load_data()

    df_input = st.session_state["dati_azienda"]

    num_anni = st.sidebar.number_input("Numero di anni", min_value=1, max_value=10, value=int(len(df_input)) if not df_input.empty else 4)

    anni = [st.sidebar.number_input(f"Anno {i + 1}", min_value=2000, max_value=2100,
                                     value=int(df_input.iloc[i]["anno"]) if i < len(df_input) else 2020 + i,
                                     key=f"anno_{i}") for i in range(num_anni)]
    ricavi = [st.sidebar.number_input(f"Ricavi Anno {anni[i]}", min_value=0.0, step=1000.0,
                                       value=float(df_input.iloc[i]["ricavi"]) if i < len(df_input) else 1000000.0,
                                       key=f"ricavi_{i}") for i in range(num_anni)]
    costi = [st.sidebar.number_input(f"Costi Anno {anni[i]}", min_value=0.0, step=1000.0,
                                      value=float(df_input.iloc[i]["costi"]) if i < len(df_input) else 1000000.0,
                                      key=f"costi_{i}") for i in range(num_anni)]

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
        requests.delete(f'{SUPABASE_URL}/rest/v1/dati_finanziari?anno=gt.0', headers=headers)
        for _, dati in df_input.iterrows():
            requests.post(f'{SUPABASE_URL}/rest/v1/dati_finanziari', headers=headers, json=dati.to_dict())

        st.session_state["dati_azienda"] = load_data()
        st.success("✅ Dati salvati correttamente!")
        st.experimental_rerun()

    st.write("### 📋 Dati Inseriti e Indicatori")
    st.dataframe(df_input)

with tab2:
    st.header("📊 Dashboard Aziendale")
    df = st.session_state["dati_azienda"]
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ricavi Totali", f"{df['ricavi'].sum():,.0f} €")
        col2.metric("📉 Costi Totali", f"{df['costi'].sum():,.0f} €")
        col3.metric("💹 Utile Totale", f"{df['utile_netto'].sum():,.0f} €")

        col4, col5 = st.columns(2)
        col4.metric("📈 Margine Medio", f"{df['margine'].mean():.2f} %")
        col5.metric("📊 Crescita Utile Media", f"{df['crescita'].mean():.2f} %")

        st.markdown("---")

        fig_dash, ax_dash = plt.subplots(figsize=(10, 4))
        ax_dash.bar(df['anno'], df['ricavi'], color='blue', label='Ricavi')
        ax_dash.bar(df['anno'], df['costi'], color='red', label='Costi', bottom=df['ricavi'] - df['costi'])
        ax_dash.bar(df['anno'], df['utile_netto'], color='green', label='Utile Netto')
        ax_dash.set_title("Andamento Ricavi, Costi e Utile Netto")
        ax_dash.set_xlabel("Anno")
        ax_dash.set_ylabel("Valore (€)")
        ax_dash.legend()
        ax_dash.grid(True)
        st.pyplot(fig_dash)
        st.session_state["fig_dashboard"] = fig_dash

with tab3:
    df = st.session_state["dati_azienda"]
    if not df.empty:
        st.write("### 📊 Grafico a barre: Ricavi, Costi e Utile Netto")
        fig_bar, ax = plt.subplots(figsize=(10, 5))
        bar_width = 0.3
        index = range(len(df['anno']))
        ax.bar([i - bar_width for i in index], df['ricavi'], width=bar_width, color='blue', label='Ricavi')
        ax.bar(index, df['costi'], width=bar_width, color='red', label='Costi')
        ax.bar([i + bar_width for i in index], df['utile_netto'], width=bar_width, color='green', label='Utile Netto')
        ax.set_xticks(index)
        ax.set_xticklabels(df['anno'])
        ax.set_xlabel("Anno")
        ax.set_ylabel("Valore (€)")
        ax.legend()
        st.pyplot(fig_bar)

        st.write("### 📈 Grafico a linee: Utile Netto")
        fig_line, ax_line = plt.subplots(figsize=(10, 4))
        ax_line.plot(df['anno'], df['utile_netto'], marker="o", linestyle='-', color="green", linewidth=2)
        ax_line.set_title("Andamento dell'Utile Netto")
        ax_line.set_xlabel("Anno")
        ax_line.set_ylabel("Utile Netto (€)")
        ax_line.grid(True)
        st.pyplot(fig_line)

        st.session_state["fig_bar"] = fig_bar
        st.session_state["fig_line"] = fig_line

with tab4:
    df = st.session_state["dati_azienda"]
    st.write("### 📄 Scarica i report in PDF")

    # PDF TABELLA DATI
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
    st.download_button("📥 Scarica PDF Dati", dati_pdf, file_name="dati_finanziari.pdf", mime="application/pdf")

    # PDF GRAFICI
    grafici_buffer = BytesIO()
    with PdfPages(grafici_buffer) as pdf:
        pdf.savefig(st.session_state["fig_bar"], bbox_inches='tight')
        pdf.savefig(st.session_state["fig_line"], bbox_inches='tight')
        pdf.savefig(st.session_state["fig_dashboard"], bbox_inches='tight')
    grafici_pdf = grafici_buffer.getvalue()
    st.download_button("📥 Scarica PDF Grafici", grafici_pdf, file_name="grafici_finanziari.pdf", mime="application/pdf")
