import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
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
st.set_page_config(page_title="Analisi Finanziaria", layout="wide")
st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")

# Caricamento dati da Supabase
def load_data():
    response = requests.get(f'{SUPABASE_URL}/rest/v1/dati_finanziari?select=*', headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.drop(columns=["data"], errors='ignore')
        df["anno"] = df["anno"].astype(int)
        return df.sort_values("anno") if not df.empty else pd.DataFrame()
    else:
        st.error("Errore nel recupero dati")
        return pd.DataFrame()

# Carica dati completi
df = load_data()
df_originale = df.copy()

# Modifica selezione anni con multiselect
anni_disponibili = sorted(df_originale["anno"].unique().tolist())
anni_selezionati = st.sidebar.multiselect(
    "Seleziona gli anni da analizzare:", 
    options=anni_disponibili, 
    default=anni_disponibili
)

# Applica filtro per visualizzazione, ma non per salvataggio
if anni_selezionati:
    df = df_originale[df_originale["anno"].isin(anni_selezionati)]
else:
    df = df_originale.copy()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "📊 Dashboard", "📈 Grafici", "📄 PDF"])

with tab1:
    st.subheader("Inserimento Dati")
with st.form("form_inserimento"):
    col1, col2 = st.columns(2)
    with col1:
        anno = st.number_input("Anno", min_value=2000, max_value=2100, step=1)
    with col2:
        elimina = st.form_submit_button("❌ Elimina Dati")

    ricavi = st.number_input("Ricavi (€)", min_value=0.0, step=1000.0)
    costi = st.number_input("Costi (€)", min_value=0.0, step=1000.0)

    utile = ricavi - costi
    margine = (utile / ricavi * 100) if ricavi else 0

    anno_precedente = df_originale[df_originale["anno"] == anno - 1]
    if not anno_precedente.empty:
        utile_precedente = anno_precedente["utile_netto"].values[0]
        if utile_precedente != 0 and pd.notna(utile_precedente):
            crescita = ((utile - utile_precedente) / utile_precedente) * 100
        else:
            crescita = 0
    else:
        crescita = 0

    st.info(f"Utile Netto: € {utile:,.2f} | Margine: {margine:.2f} % | Crescita: {crescita:.2f} %")

    salva = st.form_submit_button("💾 Salva dati")

    if salva:
        if ricavi == 0:
            st.warning("⚠️ I ricavi devono essere maggiori di zero.")
        elif anno in df_originale["anno"].values:
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

    if elimina:
        res = requests.delete(
            f"{SUPABASE_URL}/rest/v1/dati_finanziari?anno=eq.{int(anno)}",
            headers=headers
        )
        if res.status_code == 204:
            st.success(f"✅ Dati per l'anno {int(anno)} eliminati con successo.")
            st.rerun()
        else:
            st.error("❌ Errore nell'eliminazione dei dati.")

                
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