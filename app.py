import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("📊 Analisi Finanziaria - Serramenti Renato Orrù")
    
    st.sidebar.header("Inserisci i dati")
    
    # Input dati
    anni = st.sidebar.text_area("Anni (separati da virgola)", "2019, 2020, 2021, 2022")
    ricavi = st.sidebar.text_area("Ricavi (separati da virgola)", "1440316, 1585005, 2750442, 4413220")
    costi = st.sidebar.text_area("Costi (separati da virgola)", "1440184, 1572838, 2651845, 3556270")
    
    # Converti i dati
    try:
        anni = [int(x.strip()) for x in anni.split(",")]
        ricavi = [float(x.strip()) for x in ricavi.split(",")]
        costi = [float(x.strip()) for x in costi.split(",")]
        utile_netto = [r - c for r, c in zip(ricavi, costi)]
        
        df = pd.DataFrame({"Anno": anni, "Ricavi": ricavi, "Costi": costi, "Utile Netto": utile_netto})
        
        # Mostra i dati
        st.write("### Dati inseriti:", df)
        
        # Grafico
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
        ax.legend()
        st.pyplot(fig)
        
        # Esporta CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica i dati in CSV", data=csv, file_name="dati_finanziari.csv", mime="text/csv")
        
    except ValueError:
        st.error("⚠️ Assicurati di inserire i dati nel formato corretto!")

if __name__ == "__main__":
    main()
