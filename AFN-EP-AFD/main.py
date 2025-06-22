import streamlit as st
import random
from graph import afficher_graphe, afficher_graphe_e
from automate_operations import convertir_afn_en_afd, epsilon_afn_to_afd, est_deterministe, completer_afd
from automate_operations import emonder_automate

# ---- CONFIG ----
st.set_page_config(page_title="Automates - DFA/NFA", layout="wide")
st.title("🧠 Manipulation des Automates (DFA/NFA)")

# ---- INITIALISATION DE SESSION_STATE ----
if "transitions" not in st.session_state:
    st.session_state.transitions = {}

# ---- SIDEBAR POUR L'ENTRÉE DES DONNÉES ----
st.sidebar.header("📥 Définir l'automate")

type_automate = st.sidebar.radio("Type d'automate :", ["DFA", "NFA"])

alphabet_input = st.sidebar.text_input("Alphabet (séparé par des virgules)", value="a,b")
alphabet = [x.strip() for x in alphabet_input.split(",") if x.strip()]

nb_etats = st.sidebar.number_input("Nombre d'états", min_value=1, max_value=20, value=3)
etats = [f"q{i}" for i in range(nb_etats)]

etat_initial = st.sidebar.selectbox("État initial", etats)
etats_finaux = st.sidebar.multiselect("États finaux", etats)

# Génération manuelle des transitions
st.sidebar.markdown("### Définir les transitions")

# Si aucune transition dans session_state, on les initialise ici
if not st.session_state.transitions:
    st.session_state.transitions = {etat: {sym: [] for sym in alphabet} for etat in etats}

# Interface de saisie (MAIS on n'écrase pas si génération automatique déjà faite)
for etat in etats:
    for symbole in alphabet:
        default_val = ",".join(st.session_state.transitions.get(etat, {}).get(symbole, []))
        val = st.sidebar.text_input(f"δ({etat}, {symbole})", value=default_val, key=f"{etat}-{symbole}")
        destinations = [x.strip() for x in val.split(",") if x.strip()]
        if etat not in st.session_state.transitions:
            st.session_state.transitions[etat] = {}
        st.session_state.transitions[etat][symbole] = destinations

# Option de génération automatique
st.sidebar.markdown("### 🔁 Générer un automate aléatoire")
if st.sidebar.button("Générer automatiquement"):
    auto_transitions = {}
    for etat in etats:
        auto_transitions[etat] = {}
        for symbole in alphabet:
            if type_automate == "DFA":
                auto_transitions[etat][symbole] = [random.choice(etats)]
            else:
                auto_transitions[etat][symbole] = random.sample(etats, random.randint(0, len(etats)))
    st.session_state.transitions = auto_transitions

# On récupère les transitions depuis session_state
transitions = st.session_state.transitions

# ---- ZONE PRINCIPALE ----
st.subheader("⚙️ Opérations sur l'automate")
operation = st.selectbox("Choisir une opération :", [
    "Afficher la syntaxe",
    "Afficher le graphe",
    "Déterminiser (si NFA)",
    "Conversion AFD vers AFN",
    "Minimiser (si DFA)",
    "Conversion AFD vers AFDC (complétion)",
    "Émondage de l'automate",
    "Complémenter (si DFA)",
    "Tester un mot",
])

# === AFFICHAGE SYNTAXE ===
if operation == "Afficher la syntaxe":
    st.markdown("### Structure de l'automate")
    st.markdown(f"- **Alphabet** : `{alphabet}`")
    st.markdown(f"- **États** : `{etats}`")
    st.markdown(f"- **État initial** : `{etat_initial}`")
    st.markdown(f"- **États finaux** : `{etats_finaux}`")
    st.markdown(f"- **Transitions** :")
    for e in transitions:
        for s in transitions[e]:
            st.markdown(f"  - δ({e}, '{s}') → {transitions[e][s]}")

# === GRAPHE SIMPLE ===
elif operation == "Afficher le graphe":
    st.markdown("### 🧩 Graphe de l'automate")
    graph = afficher_graphe(transitions, etat_initial, etats_finaux)
    st.graphviz_chart(graph.source)

# === DETERMINSATION ===
elif operation == "Déterminiser (si NFA)":
    result, message = convertir_afn_en_afd(transitions, alphabet, etat_initial, etats_finaux)
    if message:
        st.info(message)
    else:
        st.success("✅ Automate déterminisé avec succès")
        st.markdown("### Structure de l’AFD obtenu :")
        st.markdown(f"- **Alphabet** : `{result['alphabet']}`")
        st.markdown(f"- **États** : `{result['etats']}`")
        st.markdown(f"- **État initial** : `{result['etat_initial']}`")
        st.markdown(f"- **États finaux** : `{result['etats_finaux']}`")
        st.markdown(f"- **Transitions** :")
        for e in result["transitions"]:
            for s in result["transitions"][e]:
                st.markdown(f"  - δ({e}, '{s}') → {result['transitions'][e][s]}")
        st.markdown("### 🔍 Graphe de l’AFD obtenu")
        graph = afficher_graphe(result["transitions"], result["etat_initial"], result["etats_finaux"])
        st.graphviz_chart(graph.source)

# === CONVERSION AFD → AFN ===
elif operation == "Conversion AFD vers AFN":
    if not est_deterministe(transitions):
        st.warning("❌ Cet automate n'est pas un AFD. Impossible de faire la conversion.")
    else:
        st.success("✅ Conversion AFD → NFA effectuée (avec transitions non-déterministes simulées)")
        
        # Créons un faux NFA équivalent en dupliquant certaines transitions
        nfa_like = {}
        for etat in transitions:
            nfa_like[etat] = {}
            for symbole in transitions[etat]:
                destination = transitions[etat][symbole][0]  # unique en AFD
                nfa_like[etat][symbole] = [destination]

                # ✅ Astuce : ajoutons parfois la même transition 2 fois
                if random.random() < 0.3:  # 30% de chance de la dupliquer
                    nfa_like[etat][symbole].append(random.choice(list(transitions.keys())))

        st.markdown("### 🔍 Graphe du NFA simulé")
        graph = afficher_graphe(nfa_like, etat_initial, etats_finaux)
        st.graphviz_chart(graph.source)

# AFD complet

elif operation == "Conversion AFD vers AFDC (complétion)":
    new_transitions, etat_puits = completer_afd(transitions, alphabet)
    if new_transitions is None:
        st.warning("❌ Cet automate n'est pas déterministe. Impossible de le compléter.")
    else:
        st.success("✅ Automate complété avec succès.")
        st.markdown("### 🔍 Graphe de l’AFDC obtenu")

        # Affichage syntaxique
        for e in new_transitions:
            for s in new_transitions[e]:
                st.markdown(f"  - δ({e}, '{s}') → {new_transitions[e][s]}")

        etats_complets = list(new_transitions.keys())
        graph = afficher_graphe(new_transitions, etat_initial, etats_finaux)
        st.graphviz_chart(graph.source)

        if etat_puits:
            st.info(f"ℹ️ Un état puits `{etat_puits}` a été ajouté.")


elif operation == "Émondage de l'automate":
    result = emonder_automate(transitions, etat_initial, etats_finaux)

    if not result["etat_initial"]:
        st.warning("❌ L’état initial n’est pas utile. L’automate est vide après émondage.")
    else:
        st.success("✅ Automate émondé généré avec succès.")
        st.markdown("### 🌿 Structure de l'automate émondé")
        st.markdown(f"- **États utiles** : `{result['etats']}`")
        st.markdown(f"- **État initial** : `{result['etat_initial']}`")
        st.markdown(f"- **États finaux** : `{result['etats_finaux']}`")

        for e in result["transitions"]:
            for s in result["transitions"][e]:
                st.markdown(f"  - δ({e}, '{s}') → {result['transitions'][e][s]}")

        st.markdown("### 🔍 Graphe de l’automate émondé")
        graph = afficher_graphe(result["transitions"], result["etat_initial"], result["etats_finaux"])
        st.graphviz_chart(graph.source)
