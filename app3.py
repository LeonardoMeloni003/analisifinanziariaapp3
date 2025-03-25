import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

# --- CONFIGURAZIONE ---
PASSWORD = "analisi2024"

# --- LOGIN ---
def check_password()

# --- SFONDO BUSINESS ELEGANTE ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4f7fa 0%, #d9e2ec 100%);
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
):
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

# --- SIDEBAR PER INPUT ---
st.sidebar.header("Inserisci i dati")

# Numero di anni da analizzare
num_anni = st.sidebar.number_input("Numero di anni", min_value=1, max_value=10, value=4)

# Inserimento degli anni
anni = []
for i in range(num_anni):
    anno = st.sidebar.number_input(f"Anno {i + 1}", min_value=2000, max_value=2100, value=2020 + i)
    anni.append(anno)

# Inserimento dei ricavi
ricavi = []
for i in range(num_anni):
    ricavo = st.sidebar.number_input(f"Ricavi Anno {anni[i]}", min_value=0, value=1000000)
    ricavi.append(ricavo)

# Inserimento dei costi
costi = []
for i in range(num_anni):
    costo = st.sidebar.number_input(f"Costi Anno {anni[i]}", min_value=0, value=1000000)
    costi.append(costo)

# Calcolo dell'utile netto
utile_netto = [r - c for r, c in zip(ricavi, costi)]

# --- INDICATORI FINANZIARI ---
# Margine di profitto: utile netto / ricavi
margine_profitto = [(u / r * 100) if r != 0 else 0 for u, r in zip(utile_netto, ricavi)]

# Crescita % utile netto anno su anno
crescita_utile = [0]
for i in range(1, len(utile_netto)):
    prec = utile_netto[i - 1]
    crescita = ((utile_netto[i] - prec) / prec * 100) if prec != 0 else 0
    crescita_utile.append(crescita)

# --- CREAZIONE DEL DATAFRAME COMPLETO ---
df = pd.DataFrame({
    "Anno": anni,
    "Ricavi": ricavi,
    "Costi": costi,
    "Utile Netto": utile_netto,
    "Margine di Profitto (%)": margine_profitto,
    "Crescita Utile Netto (%)": crescita_utile
})

# --- SALVATAGGIO IN MEMORIA SESSIONE ---
st.session_state["dati_azienda"] = df

# Visualizzazione tabella
st.write("### 📋 Dati Inseriti e Indicatori")
st.dataframe(df)

# --- GRAFICO A BARRE ---
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

# --- GRAFICO A LINEE DELL'UTILE NETTO ---
st.write("### 📈 Andamento Utile Netto")

try:
    fig_line, ax_line = plt.subplots(figsize=(10, 4))
    fig_line.suptitle("Serramenti Renato Orrù", fontsize=14)
    ax_line.plot(anni, utile_netto, marker="o", linestyle='-', color="green", linewidth=2)
    ax_line.set_title("Andamento dell'Utile Netto")
    ax_line.set_xlabel("Anno")
    ax_line.set_ylabel("Utile Netto (€)")
    ax_line.grid(True)

    st.pyplot(fig_line)
except Exception as e:
    st.error(f"❌ Errore nella generazione del grafico a linee: {e}")

# --- DOWNLOAD GRAFICI IN PDF ---
pdf_buffer = BytesIO()
with PdfPages(pdf_buffer) as pdf:
    pdf.savefig(fig)
    pdf.savefig(fig_line)

st.download_button(
    label="📄 Scarica grafici in PDF",
    data=pdf_buffer.getvalue(),
    file_name="grafici_analisi_finanziaria.pdf",
    mime="application/pdf"
)
