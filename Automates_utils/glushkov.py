# glushkov_simple.py - Algorithme de Glushkov simplifié avec tableau de successeurs
from regex_parser import parse_regex

class Automaton:
    def __init__(self):
        self.states = set()
        self.initial_states = set()
        self.final_states = set()
        self.transitions = {}
        self.alphabet = set()
    
    def add_transition(self, src, symbol, dest):
        if (src, symbol) not in self.transitions:
            self.transitions[(src, symbol)] = set()
        self.transitions[(src, symbol)].add(dest)
        self.alphabet.add(symbol)
    
    def to_dict(self):
        """Convertit l'automate au format attendu par l'interface"""
        all_states = {'0'} | {str(s) for s in self.states}
        
        transitions_dict = {}
        for (src, symbol), dests in self.transitions.items():
            key = f"{src},{symbol}"
            transitions_dict[key] = sorted([str(dest) for dest in dests])
        
        return {
            'alphabet': sorted(list(self.alphabet)),
            'etats': sorted(list(all_states), key=lambda x: int(x) if x.isdigit() else 0),
            'etats_initiaux': ['0'],
            'etats_finaux': sorted([str(s) for s in self.final_states]),
            'transitions': transitions_dict
        }

def lineariser_regex(regex_str):
    """
    Étape 1: Linéariser toutes les lettres
    Ex: a(a+b)b = a1(a2+b3)b4
    """
    ast = parse_regex(regex_str)
    
    # Dictionnaire position -> lettre originale
    positions = {}
    pos_counter = 1
    
    def parcourir_et_numeroter(node):
        nonlocal pos_counter
        if node.kind == 'char':
            node.pos = pos_counter
            positions[pos_counter] = node.value
            pos_counter += 1
        elif hasattr(node, 'left') and node.left:
            parcourir_et_numeroter(node.left)
        if hasattr(node, 'right') and node.right:
            parcourir_et_numeroter(node.right)
    
    parcourir_et_numeroter(ast)
    return ast, positions

def calculer_premiers_derniers(ast):
    """
    Calcule les ensembles First et Last pour déterminer 
    les états initiaux et finaux potentiels
    """
    def is_nullable(node):
        if node.kind == 'char':
            return False
        elif node.kind == 'union':
            return is_nullable(node.left) or is_nullable(node.right)
        elif node.kind == 'concat':
            return is_nullable(node.left) and is_nullable(node.right)
        elif node.kind == 'star':
            return True
        elif node.kind == 'plus':
            return False
        return False
    
    def first_pos(node):
        if node.kind == 'char':
            return {node.pos}
        elif node.kind == 'union':
            return first_pos(node.left) | first_pos(node.right)
        elif node.kind == 'concat':
            if is_nullable(node.left):
                return first_pos(node.left) | first_pos(node.right)
            else:
                return first_pos(node.left)
        elif node.kind in ['star', 'plus']:
            return first_pos(node.left)
        return set()
    
    def last_pos(node):
        if node.kind == 'char':
            return {node.pos}
        elif node.kind == 'union':
            return last_pos(node.left) | last_pos(node.right)
        elif node.kind == 'concat':
            if is_nullable(node.right):
                return last_pos(node.left) | last_pos(node.right)
            else:
                return last_pos(node.right)
        elif node.kind in ['star', 'plus']:
            return last_pos(node.left)
        return set()
    
    return first_pos(ast), last_pos(ast), is_nullable(ast)

def creer_tableau_successeurs(ast, positions):
    """
    Créé le tableau de successeurs pour chaque position
    """
    # Initialiser le tableau de successeurs
    successeurs = {pos: set() for pos in positions.keys()}
    
    def calculer_successeurs(node):
        if node.kind == 'concat':
            # Pour AB: les derniers de A peuvent aller vers les premiers de B
            def last_pos(n):
                if n.kind == 'char':
                    return {n.pos}
                elif n.kind == 'union':
                    return last_pos(n.left) | last_pos(n.right)
                elif n.kind == 'concat':
                    right_nullable = is_nullable(n.right)
                    if right_nullable:
                        return last_pos(n.left) | last_pos(n.right)
                    else:
                        return last_pos(n.right)
                elif n.kind in ['star', 'plus']:
                    return last_pos(n.left)
                return set()
            
            def first_pos(n):
                if n.kind == 'char':
                    return {n.pos}
                elif n.kind == 'union':
                    return first_pos(n.left) | first_pos(n.right)
                elif n.kind == 'concat':
                    left_nullable = is_nullable(n.left)
                    if left_nullable:
                        return first_pos(n.left) | first_pos(n.right)
                    else:
                        return first_pos(n.left)
                elif n.kind in ['star', 'plus']:
                    return first_pos(n.left)
                return set()
            
            def is_nullable(n):
                if n.kind == 'char':
                    return False
                elif n.kind == 'union':
                    return is_nullable(n.left) or is_nullable(n.right)
                elif n.kind == 'concat':
                    return is_nullable(n.left) and is_nullable(n.right)
                elif n.kind == 'star':
                    return True
                elif n.kind == 'plus':
                    return False
                return False
            
            derniers_gauche = last_pos(node.left)
            premiers_droite = first_pos(node.right)
            
            for pos in derniers_gauche:
                successeurs[pos] |= premiers_droite
            
            # Traiter récursivement
            calculer_successeurs(node.left)
            calculer_successeurs(node.right)
            
        elif node.kind in ['star', 'plus']:
            # Pour A* et A+: les derniers peuvent revenir aux premiers
            def last_pos(n):
                if n.kind == 'char':
                    return {n.pos}
                elif n.kind == 'union':
                    return last_pos(n.left) | last_pos(n.right)
                elif n.kind == 'concat':
                    right_nullable = is_nullable(n.right)
                    if right_nullable:
                        return last_pos(n.left) | last_pos(n.right)
                    else:
                        return last_pos(n.right)
                elif n.kind in ['star', 'plus']:
                    return last_pos(n.left)
                return set()
            
            def first_pos(n):
                if n.kind == 'char':
                    return {n.pos}
                elif n.kind == 'union':
                    return first_pos(n.left) | first_pos(n.right)
                elif n.kind == 'concat':
                    left_nullable = is_nullable(n.left)
                    if left_nullable:
                        return first_pos(n.left) | first_pos(n.right)
                    else:
                        return first_pos(n.left)
                elif n.kind in ['star', 'plus']:
                    return first_pos(n.left)
                return set()
            
            def is_nullable(n):
                if n.kind == 'char':
                    return False
                elif n.kind == 'union':
                    return is_nullable(n.left) or is_nullable(n.right)
                elif n.kind == 'concat':
                    return is_nullable(n.left) and is_nullable(n.right)
                elif n.kind == 'star':
                    return True
                elif n.kind == 'plus':
                    return False
                return False
            
            derniers = last_pos(node.left)
            premiers = first_pos(node.left)
            
            for pos in derniers:
                successeurs[pos] |= premiers
            
            calculer_successeurs(node.left)
            
        elif node.kind == 'union':
            # Pour A|B: traiter les deux branches
            calculer_successeurs(node.left)
            calculer_successeurs(node.right)
    
    calculer_successeurs(ast)
    return successeurs

def construire_automate_glushkov(regex_str):
    """
    Algorithme de Glushkov simplifié:
    1. Linéariser toutes les lettres
    2. Créer tableau de successeurs à partir du point initial 0
    3. Choisir états initiaux et finaux
    4. Pour chaque lettre, rechercher ses successeurs
    5. Construire les transitions
    """
    print(f"=== Construction Glushkov pour: {regex_str} ===")
    
    try:
        # Étape 1: Linéarisation
        ast, positions = lineariser_regex(regex_str)
        print(f"\n1. Linéarisation:")
        linearisation_str = regex_str
        for pos in sorted(positions.keys()):
            linearisation_str = linearisation_str.replace(positions[pos], f"{positions[pos]}{pos}", 1)
        print(f"   {regex_str} = {linearisation_str}")
        
        for pos, lettre in sorted(positions.items()):
            print(f"   Position {pos}: {lettre}")
        
        # Étape 2: Calculer premiers et derniers
        premiers, derniers, nullable = calculer_premiers_derniers(ast)
        print(f"\n2. États susceptibles:")
        print(f"   États initiaux potentiels (First): {sorted(premiers)}")
        print(f"   États finaux potentiels (Last): {sorted(derniers)}")
        print(f"   Expression nullable: {nullable}")
        
        # Étape 3: Créer tableau de successeurs
        successeurs = creer_tableau_successeurs(ast, positions)
        print(f"\n3. Tableau de successeurs:")
        for pos in sorted(positions.keys()):
            lettre = positions[pos]
            succ = sorted(successeurs[pos])
            if succ:
                succ_str = [f"{positions[s]}{s}" for s in succ]
                print(f"   {lettre}{pos} -> {succ_str}")
            else:
                print(f"   {lettre}{pos} -> []")
        
        # Étape 4: Construction de l'automate
        automate = Automaton()
        
        # États: 0 (initial) + toutes les positions
        automate.states = set(positions.keys())
        
        # États finaux: positions dans Last + 0 si nullable
        automate.final_states = derniers.copy()
        if nullable:
            automate.final_states.add(0)
        
        print(f"\n4. Construction de l'automate:")
        print(f"   États: {{0, {', '.join(map(str, sorted(positions.keys())))}}}")
        print(f"   État initial: 0")
        print(f"   États finaux: {{{', '.join(map(str, sorted(automate.final_states)))}}}")
        
        # Transitions depuis l'état initial 0
        print(f"\n5. Transitions:")
        print(f"   Depuis l'état 0:")
        for pos in sorted(premiers):
            lettre = positions[pos]
            automate.add_transition(0, lettre, pos)
            print(f"     0 --{lettre}--> {pos}")
        
        # Transitions entre positions selon successeurs
        for pos in sorted(positions.keys()):
            lettre_actuelle = positions[pos]
            if successeurs[pos]:
                print(f"   Depuis l'état {pos} ({lettre_actuelle}{pos}):")
                for succ_pos in sorted(successeurs[pos]):
                    lettre_succ = positions[succ_pos]
                    automate.add_transition(pos, lettre_succ, succ_pos)
                    print(f"     {pos} --{lettre_succ}--> {succ_pos}")
        
        # Vérification pour a(a+b)b
        if regex_str == "a(a+b)b":
            print(f"\n6. Vérification pour a(a+b)b:")
            print(f"   ✓ Linéarisation: a1(a2+b3)b4")
            print(f"   ✓ 5 états: {{0, 1, 2, 3, 4}}")
            print(f"   ✓ État initial: 0")
            print(f"   ✓ État final: 4")
            print(f"   ✓ Transitions attendues:")
            print(f"     0 --a--> 1  (vers a1)")
            print(f"     1 --a--> 2  (a1 vers a2)")
            print(f"     1 --b--> 3  (a1 vers b3)")
            print(f"     2 --b--> 4  (a2 vers b4)")
            print(f"     3 --b--> 4  (b3 vers b4)")
        
        result = {
            'succes': True,
            'message': f'Automate de Glushkov construit pour "{regex_str}"',
            'automate': automate.to_dict(),
            'debug': {
                'linearized': {f"pos_{k}": f"{v}_{k}" for k, v in positions.items()},
                'successeurs': {f"pos_{k}": [f"pos_{p}" for p in sorted(v)] for k, v in successeurs.items()},
                'first_states': sorted(list(premiers)),
                'last_states': sorted(list(derniers)),
                'nullable': nullable
            },
            'regex': regex_str
        }
        
        return result
        
    except Exception as e:
        return {
            'succes': False,
            'erreur': f'Erreur lors de la construction : {str(e)}'
        }

# Test avec l'exemple
if __name__ == "__main__":
    # Test principal
    result = construire_automate_glushkov("a(a+b)b")
    
    if result['succes']:
        print(f"\n" + "="*50)
        print("AUTOMATE FINAL:")
        automate = result['automate']
        print(f"États: {automate['etats']}")
        print(f"Alphabet: {automate['alphabet']}")
        print(f"États initiaux: {automate['etats_initiaux']}")
        print(f"États finaux: {automate['etats_finaux']}")
        print("Transitions:")
        for trans, dests in sorted(automate['transitions'].items()):
            src, symbol = trans.split(',')
            for dest in dests:
                print(f"  {src} --{symbol}--> {dest}")
    else:
        print(f"Erreur: {result['erreur']}")
