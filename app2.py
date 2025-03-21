import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Analisi Finanziaria")

# Aggiungi input per i dati tramite la sidebar
st.sidebar.header("Inserisci i dati")

# Input dell'utente per gli anni
anni = st.sidebar.text_area("Anni (separati da virgola)", "2019, 2020, 2021, 2022")

# Input dell'utente per i ricavi
ricavi = st.sidebar.text_area("Ricavi (separati da virgola)", "1440316, 1585005, 2750442, 4413220")

# Input dell'utente per i costi
costi = st.sidebar.text_area("Costi (separati da virgola)", "1440184, 1572838, 2651845, 3556270")

# Converti i dati inseriti
try:
    # Converti gli input in liste di numeri
    anni = [int(x.strip()) for x in anni.split(",")]
    ricavi = [float(x.strip()) for x in ricavi.split(",")]
    costi = [float(x.strip()) for x in costi.split(",")]
    
    # Calcola l'utile netto
    utile_netto = [r - c for r, c in zip(ricavi, costi)]
    
    # Crea un DataFrame con i dati
    df = pd.DataFrame({"Anno": anni, "Ricavi": ricavi, "Costi": costi, "Utile Netto": utile_netto})

    # Mostra il DataFrame all'utente
    st.write("### Dati Inseriti:")
    st.write(df)

    # Crea il grafico a barre
    fig, ax = plt.subplots(figsize=(10, 5))
    bar_width = 0.3
    index = range(len(anni))
    
    # Aggiungi barre per ricavi, costi e utile netto
    ax.bar([i - bar_width for i in index], ricavi, width=bar_width, color='blue', label='Ricavi')
    ax.bar(index, costi, width=bar_width, color='red', label='Costi')
    ax.bar([i + bar_width for i in index], utile_netto, width=bar_width, color='green', label='Utile Netto')
    
    ax.set_xticks(index)
    ax.set_xticklabels(anni)
    ax.set_xlabel("Anno")
    ax.set_ylabel("Valore (€)")
    ax.legend()
    
    st.pyplot(fig)

except ValueError:
    st.error("⚠️ Assicurati di inserire i dati nel formato corretto!")
