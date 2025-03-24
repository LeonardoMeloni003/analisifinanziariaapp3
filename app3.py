import streamlit as st

# --- CONFIGURAZIONE ---
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

# --- HOMEPAGE ---
st.title("📊 Analisi Finanziaria")
st.markdown("""
Benvenuto nell'applicazione di **analisi finanziaria**.

Usa il menu a sinistra per navigare tra le sezioni:
- 📁 Carica i tuoi dati
- 📈 Visualizza grafici
- 📄 Esporta risultati

🔐 L’accesso è protetto da password condivisa.
""")

# Esempio di layout iniziale con colonne
col1, col2 = st.columns(2)

with col1:
    st.subheader("Come iniziare")
    st.write("1. Carica il tuo file Excel o CSV\n2. Analizza i dati con i grafici\n3. Esporta il report se necessario")

with col2:
    st.image("https://static.streamlit.io/examples/dice.jpg", caption="Esempio di visualizzazione")
