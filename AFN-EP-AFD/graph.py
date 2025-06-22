# graph_automate.py
from graphviz import Digraph

def afficher_graphe(transitions, etat_initial, etats_finaux):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')

    # État initial invisible
    dot.node('', shape='none')
    dot.edge('', etat_initial)

    for etat in transitions:
        shape = 'doublecircle' if etat in etats_finaux else 'circle'
        dot.node(etat, shape=shape)

    for etat in transitions:
        for symbole in transitions[etat]:
            for dest in transitions[etat][symbole]:
                label = symbole
                dot.edge(etat, dest, label=label)

    return dot


def afficher_graphe_e(transitions, etat_initial, etats_finaux):
    dot = Digraph()

    # Ajouter les états
    for etat in transitions:
        if etat in etats_finaux:
            dot.node(etat, shape="doublecircle", style="filled", fillcolor="#e6ffe6")  # final
        else:
            dot.node(etat, shape="circle")

    # État initial fictif
    dot.node("", shape="none")
    dot.edge("", etat_initial)

    # Ajouter les transitions
    for etat in transitions:
        for symbole, destinations in transitions[etat].items():
            for dest in destinations:
                if symbole == "ε":
                    # Style particulier pour epsilon
                    dot.edge(etat, dest, label="ε", style="dashed", color="gray")
                else:
                    dot.edge(etat, dest, label=symbole)

    return dot
