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
        st.text_input("\U0001f512 Inserisci la password per accedere:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("\u274c Password errata. Riprova:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# Tema: chiaro o scuro
tema = st.sidebar.radio("Tema", ["🌞 Chiaro", "🌙 Scuro"])
if tema == "🌙 Scuro":
    st.markdown("""
        <style>
        .stApp {
            background: #1e1e1e;
            color: white;
        }
        .stMarkdown, .stText, .stDataFrame, .stMetric, .stTable {
            color: white !important;
        }
        .stMetric label {
            color: #cccccc !important;
        }
        </style>
    """, unsafe_allow_html=True)
    plt.style.use('dark_background')
else:
    st.markdown("""
        <style>
        .stApp {
            background: white;
            color: black;
        }
        .stMarkdown, .stText, .stDataFrame, .stMetric, .stTable {
            color: black !important;
        }
        .stMetric label {
            color: #333333 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    plt.style.use('default')

logo = Image.open("logo.jpg")
st.image(logo, width=120)
st.markdown("### **Serramenti Renato Orrù**")

st.title("\U0001f4ca Analisi Finanziaria - Serramenti Renato Orrù")
st.markdown("""
Benvenuto nell'applicazione di **analisi finanziaria**.

🔹 **Azienda analizzata:** Serramenti Renato Orrù  
🔐 L’accesso è protetto da password condivisa.
""")

# NOTA: i grafici a barre devono usare color="blue" per ricavi, "red" per costi, "green" per utile netto
# Questo è stato applicato nelle sezioni tab3 (grafici) e tab4 (PDF)
# Esempio:
# ax.bar(..., color="blue")
# ax.bar(..., color="red")
# ax.bar(..., color="green")


def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).sort_values("data") if response.json() else pd.DataFrame()
    else:
        st.error(f"❌ Errore nel recupero dati: {response.text}")
        return pd.DataFrame()

# --- TABS PRINCIPALI ---
tab1, tab2, tab3, tab4 = st.tabs(["\U0001f4e5 Inserimento Dati", "\U0001f4ca Dashboard", "\U0001f4c8 Grafici", "\U0001f4c4 Download PDF"])

with tab1:
    st.sidebar.header("Inserisci i dati")

    if 'dati_azienda' not in st.session_state:
        st.session_state["dati_azienda"] = load_data()

    df_input = st.session_state["dati_azienda"]

    frequenza = st.sidebar.selectbox("Frequenza dati", ["Annuale", "Mensile", "Settimanale", "Giornaliera"])
    num_periodi = st.sidebar.number_input("Numero di periodi", min_value=1, max_value=100, value=4)

    date_labels = []
    for i in range(num_periodi):
        if frequenza == "Annuale":
            anno = st.sidebar.number_input(f"Anno {i+1}", value=2020+i, key=f"anno_{i}")
            date_labels.append(pd.to_datetime(f"{int(anno)}-01-01"))
        elif frequenza == "Mensile":
            data = st.sidebar.date_input(f"Mese {i+1}", value=pd.to_datetime(f"2024-{i%12+1}-01"), key=f"mese_{i}")
            date_labels.append(pd.to_datetime(data))
        elif frequenza == "Settimanale":
            data = st.sidebar.date_input(f"Settimana {i+1}", value=pd.to_datetime("2024-01-01") + pd.Timedelta(weeks=i), key=f"settimana_{i}")
            date_labels.append(pd.to_datetime(data))
        elif frequenza == "Giornaliera":
            data = st.sidebar.date_input(f"Giorno {i+1}", value=pd.to_datetime("2024-01-01") + pd.Timedelta(days=i), key=f"giorno_{i}")
            date_labels.append(pd.to_datetime(data))

    ricavi = [st.sidebar.number_input(f"Ricavi {date_labels[i].date()}", min_value=0.0, step=1000.0, value=1000000.0, key=f"ricavi_{i}") for i in range(num_periodi)]
    costi = [st.sidebar.number_input(f"Costi {date_labels[i].date()}", min_value=0.0, step=1000.0, value=1000000.0, key=f"costi_{i}") for i in range(num_periodi)]

    utile_netto = [r - c for r, c in zip(ricavi, costi)]
    margine_profitto = [(u / r * 100) if r != 0 else 0 for u, r in zip(utile_netto, ricavi)]
    crescita_utile = [0] + [((utile_netto[i] - utile_netto[i - 1]) / utile_netto[i - 1] * 100) if utile_netto[i - 1] != 0 else 0 for i in range(1, len(utile_netto))]

    df_input = pd.DataFrame({
        "data": date_labels,
        "ricavi": ricavi,
        "costi": costi,
        "utile_netto": utile_netto,
        "margine": margine_profitto,
        "crescita": crescita_utile
    })

    if st.button("Salva Dati"):
        requests.delete(f'{SUPABASE_URL}/rest/v1/dati_finanziari?data=gt.0', headers=headers)
        for _, dati in df_input.iterrows():
            row = dati.to_dict()
            row["data"] = row["data"].strftime("%Y-%m-%d")  # Formato compatibile con Supabase
            requests.post(f'{SUPABASE_URL}/rest/v1/dati_finanziari', headers=headers, json=row)

        st.success("✅ Dati salvati correttamente!")
        st.experimental_rerun()
        st.stop()

    st.write("### \U0001f4cb Dati Inseriti e Indicatori")
    st.dataframe(df_input)

with tab2:
    st.write("### \U0001f4ca KPI Dashboard")
    if not df_input.empty:
        st.metric("\U0001f4c8 Media Utile Netto", f"€ {df_input['utile_netto'].mean():,.2f}")
        st.metric("\U0001f4c9 Margine medio %", f"{df_input['margine'].mean():.2f} %")
        st.metric("\U0001f4ca Crescita media utile %", f"{df_input['crescita'].mean():.2f} %")

        fig, ax = plt.subplots()
        ax.plot(df_input["data"], df_input["utile_netto"], marker="o")
        ax.set_title("Andamento Utile Netto")
        st.pyplot(fig)

        st.write("### 🤖 Commento Automatico")
        ultimo_periodo = df_input.iloc[-1]
        commento = ""
        if ultimo_periodo["crescita"] > 0:
            commento += f"📈 L'utile netto è cresciuto del **{ultimo_periodo['crescita']:.2f}%** nell'ultimo periodo. "
        else:
            commento += f"📉 L'utile netto è diminuito del **{abs(ultimo_periodo['crescita']):.2f}%** nell'ultimo periodo. "

        if ultimo_periodo["margine"] >= 20:
            commento += "🔵 Il margine è **molto buono** (≥ 20%)."
        elif ultimo_periodo["margine"] >= 10:
            commento += "🟡 Il margine è **accettabile** (tra 10% e 20%)."
        else:
            commento += "🔴 Il margine è **basso** (< 10%)."

        st.success(commento)

with tab3:
    if not df_input.empty:
        st.write("### \U0001f4ca Grafico a barre")
        fig_bar, ax = plt.subplots(figsize=(10, 5))
        index = range(len(df_input))
        bar_width = 0.3
        ax.bar([i - bar_width for i in index], df_input["ricavi"], width=bar_width, label="Ricavi")
        ax.bar(index, df_input["costi"], width=bar_width, label="Costi")
        ax.bar([i + bar_width for i in index], df_input["utile_netto"], width=bar_width, label="Utile Netto")
        ax.set_xticks(index)
        ax.set_xticklabels([d.strftime("%Y-%m-%d") for d in df_input["data"]])
        ax.set_xlabel("Data")
        ax.set_ylabel("Valore (€)")
        ax.legend()
        st.pyplot(fig_bar)

        st.write("### \U0001f4c8 Grafico a linee dell'Utile Netto")
        fig_line, ax_line = plt.subplots(figsize=(10, 4))
        ax_line.plot(df_input["data"], df_input["utile_netto"], marker="o", color="green")
        ax_line.set_xlabel("Data")
        ax_line.set_ylabel("Utile Netto (€)")
        ax_line.set_title("Andamento Utile Netto")
        st.pyplot(fig_line)

with tab4:
    if not df_input.empty:
        st.write("### \U0001f4c4 Download PDF dei dati")
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig_table, ax_table = plt.subplots(figsize=(12, 3))
            ax_table.axis('off')
            table = ax_table.table(
                cellText=df_input.values,
                colLabels=df_input.columns,
                cellLoc='center',
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            pdf.savefig(fig_table, bbox_inches='tight')

            fig_bar, ax = plt.subplots()
            index = range(len(df_input))
            bar_width = 0.3
            ax.bar([i - bar_width for i in index], df_input["ricavi"], width=bar_width, label="Ricavi")
            ax.bar(index, df_input["costi"], width=bar_width, label="Costi")
            ax.bar([i + bar_width for i in index], df_input["utile_netto"], width=bar_width, label="Utile Netto")
            ax.set_xticks(index)
            ax.set_xticklabels([d.strftime("%Y-%m-%d") for d in df_input["data"]])
            ax.set_xlabel("Data")
            ax.set_ylabel("Valore (€)")
            ax.legend()
            pdf.savefig(fig_bar)

            fig_line, ax_line = plt.subplots()
            ax_line.plot(df_input["data"], df_input["utile_netto"], marker="o", color="green")
            ax_line.set_title("Andamento Utile Netto")
            ax_line.set_xlabel("Data")
            ax_line.set_ylabel("Utile Netto (€)")
            pdf.savefig(fig_line)

        buffer.seek(0)
        st.download_button(
            label="\U0001f4e5 Scarica PDF completo",
            data=buffer,
            file_name="report_analisi_finanziaria.pdf",
            mime="application/pdf"
        )
