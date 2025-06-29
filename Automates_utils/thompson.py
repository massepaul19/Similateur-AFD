# thomson.py - Version corrigée selon le PDF Thompson
from collections import defaultdict

class EtatID:
    compteur = 0
    @classmethod
    def nouveau(cls):
        id_ = cls.compteur
        cls.compteur += 1
        return id_
    @classmethod
    def reset(cls):
        cls.compteur = 0

def thompson_construction(regex):
    postfix = infix_to_postfix(regex)
    stack = []
    
    for symbole in postfix:
        if symbole.isalpha():
            # Règle 2.1 : Caractère simple (a)
            # q0 --a--> q1
            e1 = EtatID.nouveau()
            e2 = EtatID.nouveau()
            transitions = {
                e1: {symbole: [e2]},
                e2: {}
            }
            stack.append((e1, [e2], transitions))
            
        elif symbole == 'ε':
            # Epsilon : état unique qui accepte directement
            e1 = EtatID.nouveau()
            transitions = {e1: {}}
            stack.append((e1, [e1], transitions))
            
        elif symbole == '*':
            # Règle 2.4 : Étoile de Kleene (R*)
            # Nouvel état initial/final avec boucle de retour
            i, finals, t = stack.pop()
            q0 = EtatID.nouveau()
            qf = EtatID.nouveau()
            
            # Copier les transitions existantes
            transitions = {}
            for etat, trans in t.items():
                transitions[etat] = dict(trans)
            
            # Ajouter les nouveaux états
            transitions[q0] = {'ε': [i, qf]}  # Vers automate interne OU accepter ε
            transitions[qf] = {}
            
            # Depuis tous les états finaux vers début ET fin
            for f in finals:
                if f not in transitions:
                    transitions[f] = {}
                if 'ε' not in transitions[f]:
                    transitions[f]['ε'] = []
                transitions[f]['ε'].extend([i, qf])  # Boucle ET sortie
            
            # Pour l'étoile, l'état initial est aussi final (accepte ε)
            stack.append((q0, [q0, qf], transitions))
            
        elif symbole == '|':
            # Règle 2.2 : Union (R1|R2)
            # Nouvel état initial avec transitions ε vers les automates
            i2, finals2, t2 = stack.pop()
            i1, finals1, t1 = stack.pop()
            q = EtatID.nouveau()
            qf = EtatID.nouveau()
            
            # Fusionner les transitions
            transitions = {}
            # Copier t1
            for etat, trans in t1.items():
                transitions[etat] = dict(trans)
            # Copier t2
            for etat, trans in t2.items():
                if etat in transitions:
                    for symb, dests in trans.items():
                        if symb in transitions[etat]:
                            transitions[etat][symb].extend(dests)
                        else:
                            transitions[etat][symb] = list(dests)
                else:
                    transitions[etat] = dict(trans)
            
            # Nouvel état initial
            transitions[q] = {'ε': [i1, i2]}
            transitions[qf] = {}
            
            # Connecter tous les états finaux au nouvel état final
            for f in finals1 + finals2:
                if f not in transitions:
                    transitions[f] = {}
                if 'ε' not in transitions[f]:
                    transitions[f]['ε'] = []
                transitions[f]['ε'].append(qf)
            
            stack.append((q, [qf], transitions))
            
        elif symbole == '.':
            # Règle 2.3 : Concaténation (R1R2)
            # L'état final de A1 devient l'état initial de A2 (FUSION)
            i2, finals2, t2 = stack.pop()
            i1, finals1, t1 = stack.pop()
            
            # Fusionner les transitions
            transitions = {}
            # Copier t1
            for etat, trans in t1.items():
                transitions[etat] = dict(trans)
            # Copier t2 en remappant i2 vers tous les finals1
            for etat, trans in t2.items():
                if etat == i2:
                    # Fusionner les transitions de i2 avec tous les états finaux de t1
                    for f1 in finals1:
                        if f1 not in transitions:
                            transitions[f1] = {}
                        for symb, dests in trans.items():
                            if symb in transitions[f1]:
                                transitions[f1][symb].extend(dests)
                            else:
                                transitions[f1][symb] = list(dests)
                else:
                    # États normaux de t2
                    if etat in transitions:
                        for symb, dests in trans.items():
                            if symb in transitions[etat]:
                                transitions[etat][symb].extend(dests)
                            else:
                                transitions[etat][symb] = list(dests)
                    else:
                        transitions[etat] = dict(trans)
            
            # Remapper les références à i2 dans les destinations
            for etat in transitions:
                for symb in transitions[etat]:
                    new_dests = []
                    for dest in transitions[etat][symb]:
                        if dest == i2:
                            new_dests.extend(finals1)
                        else:
                            new_dests.append(dest)
                    transitions[etat][symb] = new_dests
            
            stack.append((i1, finals2, transitions))
    
    if not stack:
        # Regex vide
        e = EtatID.nouveau()
        return {
            'alphabet': [],
            'etats': [str(e)],
            'etats_initiaux': [str(e)],
            'etats_finaux': [str(e)],
            'transitions': {}
        }
    
    i, finals, transitions = stack.pop()
    
    # S'assurer que tous les états référencés existent
    tous_etats = set()
    for src, arcs in transitions.items():
        tous_etats.add(src)
        for symb, dests in arcs.items():
            tous_etats.update(dests)
    
    for etat in tous_etats:
        if etat not in transitions:
            transitions[etat] = {}
    
    etats = sorted(list(transitions.keys()))
    alphabet = sorted({c for trans in transitions.values() for c in trans.keys() if c != 'ε'})
    
    return {
        'alphabet': alphabet,
        'etats': [str(e) for e in etats],
        'etats_initiaux': [str(i)],
        'etats_finaux': [str(f) for f in finals],
        'transitions': format_transitions(transitions)
    }

def format_transitions(transitions):
    formatted = {}
    for src, arcs in transitions.items():
        for symb, dests in arcs.items():
            formatted[f"{src},{symb}"] = [str(d) for d in dests]
    return formatted

def infix_to_postfix(regex):
    precedence = {'*': 3, '.': 2, '|': 1}
    output = []
    stack = []
    prev = None
    
    for char in regex:
        if char.isalpha() or char == 'ε':
            if prev and (prev.isalpha() or prev == '*' or prev == ')' or prev == 'ε'):
                while stack and stack[-1] != '(' and precedence.get('.', 0) <= precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append('.')
            output.append(char)
        elif char == '(':
            if prev and (prev.isalpha() or prev == '*' or prev == ')' or prev == 'ε'):
                while stack and stack[-1] != '(' and precedence.get('.', 0) <= precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append('.')
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()
        elif char in precedence:
            while stack and stack[-1] != '(' and precedence.get(char, 0) <= precedence.get(stack[-1], 0):
                output.append(stack.pop())
            stack.append(char)
        prev = char
    
    while stack:
        output.append(stack.pop())
    
    return output

# Test selon les exemples du PDF
def test_pdf_examples():
    EtatID.reset()
    
    print("=== Test 1: Expression 'ab' (Exemple 1 du PDF) ===")
    result = thompson_construction('ab')
    print(f"États: {result['etats']}")
    print(f"Initial: {result['etats_initiaux']}")
    print(f"Finaux: {result['etats_finaux']}")
    print(f"Transitions: {result['transitions']}")
    print()
    
    print("=== Test 2: Expression 'a*b' (Exemple 2 du PDF) ===")
    EtatID.reset()
    result = thompson_construction('a*b')
    print(f"États: {result['etats']}")
    print(f"Initial: {result['etats_initiaux']}")
    print(f"Finaux: {result['etats_finaux']}")
    print(f"Transitions: {result['transitions']}")
    print()
    
    print("=== Test 3: Expression '(a|b)*c' (Exemple 3 du PDF) ===")
    EtatID.reset()
    result = thompson_construction('(a|b)*c')
    print(f"États: {result['etats']}")
    print(f"Initial: {result['etats_initiaux']}")
    print(f"Finaux: {result['etats_finaux']}")
    print(f"Transitions: {result['transitions']}")
    print()

if __name__ == "__main__":
    test_pdf_examples()
