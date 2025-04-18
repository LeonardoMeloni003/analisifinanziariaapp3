import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import requests

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://fpblplgqvekuekorumkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwYmxwbGdxdmVrdWVrb3J1bWtyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Mjk3NjQyMCwiZXhwIjoyMDU4NTUyNDIwfQ.fwP1Y1R29VXaOJPtWOcNdliOgiGqovF87Eg0ckRgUns"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

PASSWORD = "analisi2024"

# --- AUTENTICAZIONE ---
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

# --- TEST CONNESSIONE SUPABASE ---
st.write("### 🧪 Test connessione Supabase")

try:
    test_response = requests.get(
        f"{SUPABASE_URL}/rest/v1/dati_finanziari?select=*",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )

    if test_response.status_code == 200:
        st.success("✅ Connessione a Supabase riuscita!")
        dati_test = test_response.json()
        if dati_test:
            st.write("📦 Dati ricevuti:", dati_test[:1])
        else:
            st.info("ℹ️ Connessione ok, ma nessun dato trovato.")
    else:
        st.error(f"❌ Errore nella richiesta: {test_response.status_code}")
        st.code(test_response.text)

except Exception as e:
    st.error(f"❌ Eccezione nella richiesta: {e}")


# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF", "📆 Analisi Mensile"])
# --- Caricamento dati annuali ---
@st.cache_data
def load_data_annuali():
    response = requests.get(f"{SUPABASE_URL}/rest/v1/dati_finanziari?select=*", headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if "anno" in df.columns:
            df["anno"] = df["anno"].astype(int)
        return df
    else:
        return pd.DataFrame()

df = load_data_annuali()

with tab1:
    st.subheader("Inserimento Dati")

    with st.form("form_inserimento"):
        anno = st.number_input("Anno", min_value=2000, max_value=2100, step=1)
        ricavi = st.number_input("Ricavi (€)", min_value=0.0, step=1000.0)
        costi = st.number_input("Costi (€)", min_value=0.0, step=1000.0)

        utile = ricavi - costi
        margine = (utile / ricavi * 100) if ricavi else 0

        if not df.empty and "anno" in df.columns:
            anno_precedente = df[df["anno"] == anno - 1]
            if not anno_precedente.empty:
                utile_precedente = anno_precedente["utile_netto"].values[0]
                if utile_precedente != 0 and pd.notna(utile_precedente):
                    crescita = ((utile - utile_precedente) / utile_precedente) * 100
                else:
                    crescita = 0
            else:
                crescita = 0
        else:
            crescita = 0

        st.info(f"Utile Netto: € {utile:,.2f} | Margine: {margine:.2f} % | Crescita: {crescita:.2f} %")

        submitted = st.form_submit_button("💾 Salva dati")

        if submitted:
            if ricavi == 0:
                st.warning("⚠️ I ricavi devono essere maggiori di zero.")
            elif not df.empty and "anno" in df.columns and anno in df["anno"].values:
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
    if not df.empty and "anno" in df.columns:
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
                    anno_int = int(row["anno"])
                    st.write("🛠️ Sto aggiornando l'anno:", anno_int)
                    st.write("🔁 Nuovi dati:", updated_row)
                    res = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/dati_finanziari?anno=eq.{anno_int}",
                        headers=headers,
                        json=updated_row
                    )
                    st.write("📡 Codice risposta:", res.status_code)
                    st.write("📄 Risposta server:", res.text)
                    if res.status_code == 204:
                        st.success(f"Dati aggiornati per l'anno {anno_int}")
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'aggiornamento. Controlla Supabase.")
    else:
        st.warning("⚠️ Nessun dato disponibile da modificare.")



with tab2:
    if not df.empty:
        df = df.sort_values("anno")
        df["crescita"] = [0] + [
            ((df["utile_netto"].iloc[i] - df["utile_netto"].iloc[i - 1]) / df["utile_netto"].iloc[i - 1]) * 100
            if df["utile_netto"].iloc[i - 1] != 0 and pd.notna(df["utile_netto"].iloc[i - 1])
            else 0
            for i in range(1, len(df))
        ]

        st.metric("📈 Media Utile Netto", f"€ {df['utile_netto'].mean():,.2f}")
        st.metric("📉 Margine medio %", f"{df['margine'].mean():.2f} %")
        st.metric("📊 Crescita media utile %", f"{df['crescita'].mean():.2f} %")

        st.write("### 💬 Commento automatico approfondito")
        ultimo_anno = df["anno"].max()
        ultimi_3 = df.tail(3)
        utile_trend = "🔄 Stabile"
        if len(ultimi_3) >= 3:
            if ultimi_3["utile_netto"].is_monotonic_increasing:
                utile_trend = "🟢 In crescita costante"
            elif ultimi_3["utile_netto"].is_monotonic_decreasing:
                utile_trend = "🔴 In calo costante"

        margine_medio = df["margine"].mean()
        if margine_medio > 20:
            margine_status = "🟢 Margine molto buono"
        elif margine_medio > 10:
            margine_status = "🟡 Margine nella media"
        else:
            margine_status = "🔴 Margine basso"

        crescita_medio = df["crescita"].mean()
        if crescita_medio > 5:
            crescita_status = "📈 Buona crescita media"
        elif crescita_medio > 0:
            crescita_status = "➕ Crescita lieve"
        else:
            crescita_status = "📉 Attenzione: crescita negativa"

        st.info(f"**Andamento Utile:** {utile_trend}\n\n**Margine medio:** {margine_status}\n\n**Crescita media utile netto:** {crescita_status}")
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
        st.write("### 📄 Download Report")

        # Download PDF
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            # Tabella
            fig_table, ax_table = plt.subplots(figsize=(10, 2 + len(df) * 0.25))
            ax_table.axis("off")
            formatted_df = df.copy()
            for col in formatted_df.select_dtypes(include=["float"]).columns:
                formatted_df[col] = formatted_df[col].map(lambda x: f"{x:,.2f}")
            table = ax_table.table(
                cellText=formatted_df.values,
                colLabels=formatted_df.columns,
                loc="center",
                cellLoc="center"
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            pdf.savefig(fig_table, bbox_inches="tight")
            plt.close(fig_table)

            # Grafico a Barre
            fig_bar, ax_bar = plt.subplots()
            index = range(len(df))
            ax_bar.bar([i - 0.2 for i in index], df["ricavi"], width=0.2, label="Ricavi", color="blue")
            ax_bar.bar(index, df["costi"], width=0.2, label="Costi", color="red")
            ax_bar.bar([i + 0.2 for i in index], df["utile_netto"], width=0.2, label="Utile Netto", color="green")
            ax_bar.set_xticks(index)
            ax_bar.set_xticklabels(df["anno"], rotation=45)
            ax_bar.set_xlabel("Anno")
            ax_bar.set_ylabel("Valori (€)")
            ax_bar.legend()
            pdf.savefig(fig_bar, bbox_inches="tight")
            plt.close(fig_bar)

            # Grafico Lineare
            fig_line, ax_line = plt.subplots()
            ax_line.plot(df["anno"], df["utile_netto"], marker="o", color="green")
            ax_line.set_xlabel("Anno")
            ax_line.set_ylabel("Utile Netto (€)")
            ax_line.set_title("Andamento Utile Netto")
            ax_line.grid(True)
            pdf.savefig(fig_line, bbox_inches="tight")
            plt.close(fig_line)

        buffer.seek(0)
        st.download_button("📥 Scarica PDF", buffer, "report_analisi_finanziaria.pdf")

        # Download Excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        st.download_button(
            label="📊 Scarica Excel",
            data=excel_buffer,
            file_name="analisi_finanziaria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
# --- Caricamento dati mensili ---
@st.cache_data
def load_data_mensili():
    response = requests.get(f"{SUPABASE_URL}/rest/v1/dati_mensili?select=*", headers=headers)
    if response.status_code == 200:
        df_mens = pd.DataFrame(response.json())
        if "data" in df_mens.columns:
            df_mens["data"] = pd.to_datetime(df_mens["data"], errors='coerce')
        return df_mens
    else:
        st.warning("⚠️ Errore nel recupero dati mensili")
        return pd.DataFrame()

df_mensile = load_data_mensili()

with tab5:
    st.subheader("📆 Inserimento e analisi mensile")

    with st.form("form_mensile"):
        anno = st.number_input("Anno", min_value=2000, max_value=2100, step=1)
        mesi_italiani = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
        mese = st.selectbox("Mese", options=range(1, 13), format_func=lambda x: mesi_italiani[x - 1])

        ricavi_mensili = st.number_input("Ricavi mensili (€)", min_value=0.0, step=100.0)
        costi_mensili = st.number_input("Costi mensili (€)", min_value=0.0, step=100.0)

        utile_mensile = ricavi_mensili - costi_mensili
        margine_mensile = (utile_mensile / ricavi_mensili * 100) if ricavi_mensili else 0

        # Verifica crescita rispetto al mese precedente
        if not df.empty and "anno" in df.columns and "mese" in df.columns:
            mese_precedente = df[(df["anno"] == anno) & (df["mese"] == mese - 1)]
            if not mese_precedente.empty:
                utile_precedente = mese_precedente["utile_netto_mensile"].values[0]
                if utile_precedente != 0 and pd.notna(utile_precedente):
                    crescita_mensile = ((utile_mensile - utile_precedente) / utile_precedente) * 100
                else:
                    crescita_mensile = 0
            else:
                crescita_mensile = 0
        else:
            crescita_mensile = 0

        st.info(f"Utile Netto Mensile: € {utile_mensile:,.2f} | Margine: {margine_mensile:.2f} % | Crescita: {crescita_mensile:.2f} %")

        submitted = st.form_submit_button("💾 Salva Dati Mensili")

        if submitted:
            if ricavi_mensili == 0:
                st.warning("⚠️ I ricavi devono essere maggiori di zero.")
            elif not df.empty and "anno" in df.columns and "mese" in df.columns and ((anno in df["anno"].values) and (mese in df[df["anno"] == anno]["mese"].values)):
                st.warning(f"⚠️ I dati per {mesi_italiani[mese-1]} {anno} sono già presenti.")
            else:
                nuova_riga_mensile = {
                    "anno": anno,
                    "mese": mese,
                    "ricavi_mensili": ricavi_mensili,
                    "costi_mensili": costi_mensili,
                    "utile_netto_mensile": utile_mensile,
                    "margine_mensile": margine_mensile,
                    "crescita_mensile": crescita_mensile
                }
                requests.post(f'{SUPABASE_URL}/rest/v1/dati_mensili', headers=headers, json=nuova_riga_mensile)
                st.success("✅ Dati mensili salvati con successo")
                st.rerun()

    st.write("### 📋 Dati mensili salvati")
    st.dataframe(df)

    st.write("### 🔧 Modifica Dati Mensili Esistenti")
    if not df.empty and "anno" in df.columns and "mese" in df.columns:
        for i, row in df.iterrows():
            with st.expander(f"{mesi_italiani[row['mese'] - 1]} {row['anno']}"):
                nuovo_ricavi_mensili = st.number_input(f"Ricavi (€) - {mesi_italiani[row['mese'] - 1]} {row['anno']}", value=float(row['ricavi_mensili']), step=100.0, key=f"mod_ricavi_mens_{i}")
                nuovo_costi_mensili = st.number_input(f"Costi (€) - {mesi_italiani[row['mese'] - 1]} {row['anno']}", value=float(row['costi_mensili']), step=100.0, key=f"mod_costi_mens_{i}")

                nuovo_utile_mensile = nuovo_ricavi_mensili - nuovo_costi_mensili
                nuovo_margine_mensile = (nuovo_utile_mensile / nuovo_ricavi_mensili * 100) if nuovo_ricavi_mensili else 0
                st.info(f"Utile: €{nuovo_utile_mensile:,.2f} | Margine: {nuovo_margine_mensile:.2f}%")

                if st.button(f"💾 Salva Modifiche - {mesi_italiani[row['mese'] - 1]} {row['anno']}"):
                    updated_row = {
                        "ricavi_mensili": nuovo_ricavi_mensili,
                        "costi_mensili": nuovo_costi_mensili,
                        "utile_netto_mensile": nuovo_utile_mensile,
                        "margine_mensile": nuovo_margine_mensile
                    }
                    anno_int = int(row["anno"])
                    mese_int = int(row["mese"])
                    res = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/dati_mensili?anno=eq.{anno_int}&mese=eq.{mese_int}",
                        headers=headers,
                        json=updated_row
                    )
                    if res.status_code == 204:
                        st.success(f"Dati aggiornati per {mesi_italiani[mese_int - 1]} {anno_int}")
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'aggiornamento. Controlla Supabase.")
    else:
        st.warning("⚠️ Nessun dato mensile disponibile da modificare.")
