elif operation == "Conversion epsilon-AFN vers AFD":
    if 'ε' not in alphabet:
        st.warning("❌ Cet automate ne contient pas de transitions ε.")
    else:
        result = epsilon_afn_to_afd(transitions, alphabet, etat_initial, etats_finaux)
        st.success("✅ Conversion réussie de l’epsilon-AFN vers AFD.")
        st.markdown("### Structure du DFA obtenu :")
        st.markdown(f"- **Alphabet** : `{result['alphabet']}`")
        st.markdown(f"- **États** : `{result['etats']}`")
        st.markdown(f"- **État initial** : `{result['etat_initial']}`")
        st.markdown(f"- **États finaux** : `{result['etats_finaux']}`")
        st.markdown(f"- **Transitions** :")
        for e in result["transitions"]:
            for s in result["transitions"][e]:
                st.markdown(f"  - δ({e}, '{s}') → {result['transitions'][e][s]}")

        # Affichage du graphe
        st.markdown("### 🔍 Graphe de l’AFD obtenu")
        graph = afficher_graphe(result["transitions"], result["etat_initial"], result["etats_finaux"])
        st.graphviz_chart(graph.source)