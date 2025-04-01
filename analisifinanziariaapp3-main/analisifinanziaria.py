import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Funzione per generare il report PDF
def genera_report(df):
    # Crea il PDF
    c = canvas.Canvas("report_finanziario.pdf", pagesize=letter)
    c.drawString(100, 750, "Report Finanziario - Analisi dei Dati")
    y_position = 730
    
    # Aggiungi i dati
    for i, row in df.iterrows():
        c.drawString(100, y_position, f"Anno: {row['Anno']} - Ricavi: {row['Ricavi']} - Costi: {row['Costi']}")
        y_position -= 20

    c.save()

    return "report_finanziario.pdf"


# Funzione per caricare i dati da Google Sheets
def carica_dati_da_sheets():
    # Usa le credenziali per accedere a Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Apri il foglio di calcolo
    sheet = client.open("Nome_del_foglio").sheet1

    # Carica i dati dal foglio di calcolo
    dati = sheet.get_all_records()

    return pd.DataFrame(dati)


# Funzione per calcolare il piano di rimborso del debito
def calcola_rimborso_debito(debito, tasso_interesse, anni):
    rata_mensile = (debito * tasso_interesse) / (1 - (1 + tasso_interesse) ** (-anni))
    return rata_mensile


def main():
    st.title("📊 Analisi Finanziaria Avanzata")

    st.sidebar.header("Inserisci i dati")
    
    # Input dati
    anni = st.sidebar.text_area("Anni (separati da virgola)", "2019, 2020, 2021, 2022")
    ricavi = st.sidebar.text_area("Ricavi (separati da virgola)", "1440316, 1585005, 2750442, 4413220")
    costi = st.sidebar.text_area("Costi (separati da virgola)", "1440184, 1572838, 2651845, 3556270")
    
    # Previsione dei ricavi
    st.sidebar.header("Previsione")
    debito = st.sidebar.number_input("Importo del debito (€)", 0)
    tasso_interesse = st.sidebar.number_input("Tasso di interesse (%)", 0.0)
    anni_debito = st.sidebar.number_input("Durata del debito (anni)", 1)
    
    # Converti i dati
    try:
        anni = [int(x.strip()) for x in anni.split(",")]
        ricavi = [float(x.strip()) for x in ricavi.split(",")]
        costi = [float(x.strip()) for x in costi.split(",")]
        
        # Creazione dataframe
        df = pd.DataFrame({"Anno": anni, "Ricavi": ricavi, "Costi": costi})
        
        # Creazione modello di previsione (regressione lineare)
        model = LinearRegression()
        anni_reshape = np.array(anni).reshape(-1, 1)
        model.fit(anni_reshape, ricavi)
        
        # Previsione per l'anno successivo
        anno_futuro = anni[-1] + 1
        previsione_ricavi = model.predict(np.array([[anno_futuro]]))[0]
        st.write(f"### Previsione dei ricavi per l'anno {anno_futuro}: {previsione_ricavi:.2f} €")
        
        # Mostra i dati
        st.write("### Dati inseriti:", df)
        
        # Grafico
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(anni, ricavi, color='blue', label='Ricavi storici', marker='o')
        ax.plot(anno_futuro, previsione_ricavi, color='green', marker='x', label=f'Previsione ricavi {anno_futuro}')
        ax.set_xlabel("Anno")
        ax.set_ylabel("Ricavi (€)")
        ax.legend()
        st.pyplot(fig)

        # Calcola il piano di rimborso del debito
        if debito > 0:
            tasso_interesse = tasso_interesse / 100  # Converti il tasso in formato decimale
            rata_mensile = calcola_rimborso_debito(debito, tasso_interesse, anni_debito)
            st.write(f"### Piano di rimborso debito: Rata mensile: {rata_mensile:.2f} €")

        # Genera il report PDF
        if st.button("Genera Report PDF"):
            file_pdf = genera_report(df)
            st.write(f"📄 Report generato! [Scarica il report PDF](/{file_pdf})")
        
    except ValueError:
        st.error("⚠️ Assicurati di inserire i dati nel formato corretto!")


if __name__ == "__main__":
    main()
