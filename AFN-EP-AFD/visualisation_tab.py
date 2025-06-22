import streamlit as st
import random
from graph import afficher_graphe, afficher_graphe_e
from automate_operations import convertir_afn_en_afd, epsilon_afn_to_afd, est_deterministe, completer_afd
from automate_operations import emonder_automate, minimiser_afd
def afficher_visualisation():
    st.subheader("👀 Visualisation de l'automate")

    # Récupérer les données depuis le session_state
    alphabet = st.session_state.alphabet
    etats = st.session_state.etats
    transitions = st.session_state.transitions
    etat_initial = st.session_state.etat_initial
    etats_finaux = st.session_state.etats_finaux

    action = st.selectbox("Action :", [
        "Afficher la syntaxe",
        "Afficher le graphe",
        "Déterminiser (si NFA)",
        "Conversion AFD vers AFN",
        "Conversion AFD vers AFDC (complétion)",
        "Émondage de l'automate",
        "Minimiser (si DFA)",
        "AFN → ε-AFN",
        "ε-AFN → AFN",

    ])

    if action == "Afficher la syntaxe":
        st.markdown(f"- **Alphabet** : `{alphabet}`")
        st.markdown(f"- **États** : `{etats}`")
        st.markdown(f"- **État initial** : `{etat_initial}`")
        st.markdown(f"- **États finaux** : `{etats_finaux}`")
        st.markdown("- **Transitions** :")
        for e in transitions:
            for a in transitions[e]:
                st.markdown(f"  - δ({e}, '{a}') → {transitions[e][a]}")

    elif action == "Afficher le graphe":
        graph = afficher_graphe(transitions, etat_initial, etats_finaux)
        st.graphviz_chart(graph.source)

    elif action == "Déterminiser (si NFA)":
        result, msg = convertir_afn_en_afd(transitions, alphabet, etat_initial, etats_finaux)
        if msg:
            st.warning(msg)
        else:
            st.success("✅ AFD généré")
            graph = afficher_graphe(result["transitions"], result["etat_initial"], result["etats_finaux"])
            st.graphviz_chart(graph.source)

    elif action == "Conversion AFD vers AFN":
        if not est_deterministe(transitions):
            st.warning("Ce n'est pas un AFD.")
        else:
            nfa_like = {}
            for e in transitions:
                nfa_like[e] = {}
                for a in transitions[e]:
                    nfa_like[e][a] = [transitions[e][a][0]]
                    if random.random() < 0.3:
                        nfa_like[e][a].append(random.choice(list(transitions.keys())))
            st.success("✅ AFD transformé en NFA simulé")
            graph = afficher_graphe(nfa_like, etat_initial, etats_finaux)
            st.graphviz_chart(graph.source)

    # AFD complet

    elif action == "Conversion AFD vers AFDC (complétion)":
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
    
    elif action == "Émondage de l'automate":
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

    elif action == "Minimiser (si DFA)":
        if not est_deterministe(transitions):
            st.warning("❌ Cet automate n'est pas déterministe. Impossible de minimiser.")
        else:
            result, msg = minimiser_afd(transitions, alphabet, etat_initial, etats_finaux)
            if msg:
                st.warning(msg)
            else:
                st.success("✅ Automate minimal obtenu !")
                st.markdown("### 💡 Syntaxe de l'automate minimal")
                st.markdown(f"- **États** : `{result['etats']}`")
                st.markdown(f"- **État initial** : `{result['etat_initial']}`")
                st.markdown(f"- **États finaux** : `{result['etats_finaux']}`")

                for e in result["transitions"]:
                    for a in result["transitions"][e]:
                        st.markdown(f"  - δ({e}, '{a}') → {result['transitions'][e][a]}")

                st.markdown("### 🔍 Graphe de l’automate minimal")
                graph = afficher_graphe(result["transitions"], result["etat_initial"], result["etats_finaux"])
                st.graphviz_chart(graph.source)

    elif action == "AFN → ε-AFN":
        epsilon_afn = afn_to_epsilon_afn(transitions)
        st.success("✅ Converti en ε-AFN avec succès")
        for e in epsilon_afn:
            for a in epsilon_afn[e]:
                st.markdown(f"  - δ({e}, '{a}') → {epsilon_afn[e][a]}")
        graph = afficher_graphe_e(epsilon_afn, etat_initial, etats_finaux)
        st.graphviz_chart(graph.source)

    elif action == "ε-AFN → AFN":
        afn = epsilon_afn_to_afn(transitions)
        st.success("✅ Épsilon-transitions supprimées avec succès")
        for e in afn:
            for a in afn[e]:
                st.markdown(f"  - δ({e}, '{a}') → {afn[e][a]}")
        graph = afficher_graphe(afn, etat_initial, etats_finaux)
        st.graphviz_chart(graph.source)




