import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests  # <-- Per invio dati online

# --- CONFIGURAZIONE ---
PASSWORD = "analisi2024"
SHEETBEST_URL = "https://api.sheetbest.com/sheets/30338c77-0109-4636-98fb-48337f3546d0"

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

# --- HOMEPAGE ---
st.title("📊 Analisi Finanziaria")
st.markdown("""
Benvenuto nell'applicazione di **analisi finanziaria**.

Usa il menu a sinistra per inserire i dati e visualizzare i risultati.

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

# Creazione del DataFrame
df = pd.DataFrame({"Anno": anni, "Ricavi": ricavi, "Costi": costi, "Utile Netto": utile_netto})

# Visualizzazione tabella
st.write("### 📋 Dati Inseriti")
st.dataframe(df)

# --- GRAFICO A BARRE ---
fig, ax = plt.subplots(figsize=(10, 5))
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
ax.grid(True)

st.pyplot(fig)

# --- GRAFICO A LINEE DELL'UTILE NETTO ---
st.write("### 📈 Andamento Utile Netto")

fig_line, ax_line = plt.subplots(figsize=(10, 4))
ax_line.plot(anni, utile_netto, marker="o", linestyle='-', color="green", linewidth=2)
ax_line.set_title("Andamento dell

# --- SALVATAGGIO ONLINE ---

def salva_su_google_sheet(df):
    for _, riga in df.iterrows():
        response = requests.post(
            SHEETBEST_URL,
            json=riga.to_dict()
        )
        if response.status_code == 200:
            st.success("✅ Dati salvati online con successo!")
        else:
            st.error("❌ Errore durante il salvataggio online.")

if st.button("📤 Salva dati online"):
    if "INSERISCI_LA_TUA_URL_QUA" in SHEETBEST_URL:
        st.warning("⚠️ Inserisci il tuo link Sheet.best in alto nel codice!")
    else:
        salva_su_google_sheet(df)
