import subprocess
import sys
import os
import streamlit as st
import random
from visualisation_tab import afficher_visualisation

# ---- CONFIG ----
st.set_page_config(page_title="Simulex - Automates", layout="wide")
st.title("🧠 Simulez vos Automates (DFA/NFA)")

# === DÉFINITION AUTOMATE ===
def definir_automate():
    st.sidebar.header("📥 Définir l'automate")

    st.session_state.type_automate = st.sidebar.radio("Type :", ["DFA", "NFA"])
    alphabet_input = st.sidebar.text_input("Alphabet (séparé par des virgules)", value="a,b")
    st.session_state.alphabet = [x.strip() for x in alphabet_input.split(",") if x.strip()]

    st.session_state.nb_etats = st.sidebar.number_input("Nombre d'états", 1, 20, 3)
    st.session_state.etats = [f"q{i}" for i in range(st.session_state.nb_etats)]

    st.session_state.etat_initial = st.sidebar.selectbox("État initial", st.session_state.etats)
    st.session_state.etats_finaux = st.sidebar.multiselect("États finaux", st.session_state.etats)

    st.sidebar.markdown("### Transitions")
    if "transitions" not in st.session_state:
        st.session_state.transitions = {e: {a: [] for a in st.session_state.alphabet} for e in st.session_state.etats}

    for e in st.session_state.etats:
        for a in st.session_state.alphabet:
            key = f"{e}-{a}"
            default = ",".join(st.session_state.transitions.get(e, {}).get(a, []))
            val = st.sidebar.text_input(f"δ({e}, {a})", default, key=key)
            st.session_state.transitions[e][a] = [x.strip() for x in val.split(",") if x.strip()]

    if st.sidebar.button("🔁 Générer aléatoirement"):
        auto_trans = {}
        for e in st.session_state.etats:
            auto_trans[e] = {}
            for a in st.session_state.alphabet:
                if st.session_state.type_automate == "DFA":
                    auto_trans[e][a] = [random.choice(st.session_state.etats)]
                else:
                    auto_trans[e][a] = random.sample(st.session_state.etats, random.randint(0, len(st.session_state.etats)))
        st.session_state.transitions = auto_trans

# Initialisation
definir_automate()

# === ONGLET ACTIF ===
if "onglet" not in st.session_state:
    st.session_state.onglet = "Visualisation"

# === NAVIGATION SIMPLE PAR BOUTONS ===
st.markdown("### 🔎 Navigation")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Visualisation", type="primary" if st.session_state.onglet == "Visualisation" else "secondary"):
        st.session_state.onglet = "Visualisation"

with col2:
    if st.button("Analyse", type="primary" if st.session_state.onglet == "Analyse" else "secondary"):
        st.session_state.onglet = "Analyse"

with col3:
    if st.button("Opérations", type="primary" if st.session_state.onglet == "Opérations" else "secondary"):
        st.session_state.onglet = "Opérations"

# === AFFICHAGE DU CONTENU SELON ONGLET ===
st.markdown("---")
if st.session_state.onglet == "Visualisation":
    afficher_visualisation()
elif st.session_state.onglet == "Analyse":
    st.info("🧪 Analyse à venir.")
elif st.session_state.onglet == "Opérations":
    st.info("⚙️ Opérations à venir.")

def run_streamlit_app():
    print("Démarrage du serveur Streamlit...")
    print("URL: http://localhost:5005")
    print("Arrêt: Ctrl+C")
    
    # Lancer Streamlit avec les paramètres souhaités
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "5005",
        "--server.address", "0.0.0.0",
        "--server.headless", "false"
    ])

if __name__ == '__main__':
    run_streamlit_app()
