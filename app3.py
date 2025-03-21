import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Titolo dell'app
st.title("📊 Analisi Finanziaria")

# Aggiungi input tramite la sidebar
st.sidebar.header("Inserisci i dati")

# Selezioniamo il numero di anni per il grafico
num_anni = st.sidebar.number_input("Numero di anni", min_value=1, max_value=10, value=4)

# Aggiungi gli anni tramite un input
anni = []
for i in range(num_anni):
    anno = st.sidebar.number_input(f"Anno {i + 1}", min_value=2000, max_value=2100, value=2020 + i)
    anni.append(anno)

# Aggiungi i ricavi tramite un input
ricavi = []
for i in range(num_anni):
    ricavo = st.sidebar.number_input(f"Ricavi Anno {anni[i]}", min_value=0, value=1000000)
    ricavi.append(ricavo)

# Aggiungi i costi tramite un input
costi = []
for i in range(num_anni):
    costo = st.sidebar.number_input(f"Costi Anno {anni[i]}", min_value=0, value=1000000)
    costi.append(costo)

# Calcola l'utile netto
utile_netto = [r - c for r, c in zip(ricavi, costi)]

# Crea un DataFrame per visualizzare i dati
df = pd.DataFrame({"Anno": anni, "Ricavi": ricavi, "Costi": costi, "Utile Netto": utile_netto})

# Mostra i dati in una tabella
st.write("### Dati Inseriti:")
st.write(df)

# Crea un grafico a barre
fig, ax = plt.subplots(figsize=(10, 5))
bar_width = 0.3
index = range(len(anni))

# Aggiungi le barre per Ricavi, Costi, e Utile Netto
ax.bar([i - bar_width for i in index], ricavi, width=bar_width, color='blue', label='Ricavi')
ax.bar(index, costi, width=bar_width, color='red', label='Costi')
ax.bar([i + bar_width for i in index], utile_netto, width=bar_width, color='green', label='Utile Netto')

# Etichetta degli anni
ax.set_xticks(index)
ax.set_xticklabels(anni)
ax.set_xlabel("Anno")
ax.set_ylabel("Valore (€)")
ax.legend()

# Mostra il grafico
st.pyplot(fig)
