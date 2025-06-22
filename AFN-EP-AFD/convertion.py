from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata.fa.gnfa import GNFA
import re

def convert_nfa_to_dfa():
    st.header("Conversion AFN vers AFD")
    st.write("Définissez votre AFN et convertissez-le en AFD")
    
    # Saisie des paramètres de l'AFN
    st.subheader("Définition de l'AFN")
    
    states = st.text_input("États (séparés par des virgules)", value="q0,q1,q2")
    input_symbols = st.text_input("Symboles d'entrée (séparés par des virgules)", value="a,b")
    initial_state = st.text_input("État initial", value="q0")
    final_states = st.text_input("États finaux (séparés par des virgules)", value="q2")
    
    st.subheader("Transitions (format: état,symbole→états; ex: q0,a→q1,q2)")
    transitions_input = st.text_area("Entrez les transitions (une par ligne)", 
                                   value="q0,a→q1\nq0,b→q2\nq1,a→q1\nq1,b→q1,q2\nq2,a→q1\nq2,b→q2")
    
    if st.button("Convertir en AFD"):
        try:
            # Préparation des données
            states_set = set(s.strip() for s in states.split(','))
            input_symbols_set = set(s.strip() for s in input_symbols.split(','))
            final_states_set = set(s.strip() for s in final_states.split(','))
            
            # Construction des transitions
            transitions_dict = {}
            for line in transitions_input.split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split('→')
                left = parts[0].split(',')
                state = left[0].strip()
                symbol = left[1].strip()
                targets = set(s.strip() for s in parts[1].split(','))
                
                if state not in transitions_dict:
                    transitions_dict[state] = {}
                transitions_dict[state][symbol] = targets
            
            # Création de l'AFN
            nfa = NFA(
                states=states_set,
                input_symbols=input_symbols_set,
                transitions=transitions_dict,
                initial_state=initial_state,
                final_states=final_states_set
            )
            
            # Conversion en AFD
            dfa = DFA.from_nfa(nfa)
            
            # Affichage du résultat
            st.success("AFD obtenu:")
            
            st.subheader("États")
            st.write(", ".join(sorted(dfa.states)))
            
            st.subheader("Symboles d'entrée")
            st.write(", ".join(sorted(dfa.input_symbols)))
            
            st.subheader("État initial")
            st.write(dfa.initial_state)
            
            st.subheader("États finaux")
            st.write(", ".join(sorted(dfa.final_states)))
            
            st.subheader("Transitions")
            transitions_str = []
            for state in sorted(dfa.transitions):
                for symbol in sorted(dfa.transitions[state]):
                    target = dfa.transitions[state][symbol]
                    transitions_str.append(f"{state}, {symbol} → {target}")
            st.write("\n".join(transitions_str))
            
        except Exception as e:
            st.error(f"Erreur lors de la conversion: {str(e)}")