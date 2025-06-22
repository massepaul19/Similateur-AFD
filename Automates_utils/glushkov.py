# glushkov.py - Version corrigée selon la vraie logique de Glushkov
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
        # États : 0 (initial) + positions des caractères
        all_states = {'0'} | {str(s) for s in self.states}
        
        # Transitions au format attendu
        transitions_dict = {}
        
        # Transitions normales
        for (src, symbol), dests in self.transitions.items():
            key = f"{src},{symbol}"
            if key not in transitions_dict:
                transitions_dict[key] = []
            for dest in sorted(dests):
                transitions_dict[key].append(str(dest))
        
        # Déterminer les états finaux
        final_states_list = [str(s) for s in sorted(self.final_states)]
        
        return {
            'alphabet': sorted(list(self.alphabet)),
            'etats': sorted(list(all_states), key=lambda x: int(x) if x.isdigit() else 0),
            'etats_initiaux': ['0'],
            'etats_finaux': final_states_list,
            'transitions': transitions_dict
        }

def glushkov_correct(regex):
    """Construction de l'automate de Glushkov selon la vraie logique"""
    ast = parse_regex(regex)
    
    # Étape 1: Linéarisation - Attribution des positions aux caractères
    positions = {}  # position -> caractère
    pos_counter = 1
    
    def linearize(node):
        """Linéarise l'expression en attribuant des numéros aux caractères"""
        nonlocal pos_counter
        if node.kind == 'char':
            node.pos = pos_counter
            positions[pos_counter] = node.value
            pos_counter += 1
        elif hasattr(node, 'left'):
            linearize(node.left)
            if hasattr(node, 'right') and node.right:
                linearize(node.right)
    
    linearize(ast)
    
    # Étape 2: Calcul des ensembles First, Last et Nullable
    def first_pos(node):
        """Calcule l'ensemble des premières positions"""
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
        """Calcule l'ensemble des dernières positions"""
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
    
    def is_nullable(node):
        """Détermine si un nœud peut générer le mot vide (ε)"""
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
    
    # Étape 3: Construction de la table des successeurs pour chaque position
    successors = {}  # position -> set de positions successeurs
    
    def build_successors(node):
        """Construit la table des successeurs selon la logique de Glushkov"""
        if node.kind == 'concat':
            # Pour AB: chaque position de Last(A) a pour successeurs First(B)
            last_left = last_pos(node.left)
            first_right = first_pos(node.right)
            
            for pos in last_left:
                if pos not in successors:
                    successors[pos] = set()
                successors[pos].update(first_right)
            
            build_successors(node.left)
            build_successors(node.right)
            
        elif node.kind == 'star':
            # Pour A*: chaque position de Last(A) a pour successeurs First(A)
            last_node = last_pos(node.left)
            first_node = first_pos(node.left)
            
            for pos in last_node:
                if pos not in successors:
                    successors[pos] = set()
                successors[pos].update(first_node)
            
            build_successors(node.left)
            
        elif node.kind == 'plus':
            # Pour A+: même chose que A* (A+ = AA*)
            last_node = last_pos(node.left)
            first_node = first_pos(node.left)
            
            for pos in last_node:
                if pos not in successors:
                    successors[pos] = set()
                successors[pos].update(first_node)
            
            build_successors(node.left)
            
        elif node.kind == 'union':
            # Pour A|B: traiter les deux branches
            build_successors(node.left)
            build_successors(node.right)
    
    build_successors(ast)
    
    # Initialiser les positions sans successeurs avec ensemble vide
    for pos in positions.keys():
        if pos not in successors:
            successors[pos] = set()
    
    # Étape 4: Construction de l'automate
    automaton = Automaton()
    
    # États: état initial 0 + toutes les positions
    automaton.states = set(positions.keys())
    automaton.states.add(0)
    
    # États initiaux dans First(regex) - mais transitions depuis état 0
    first_states = first_pos(ast)
    
    # États finaux: positions dans Last(regex) + état 0 si nullable
    automaton.final_states = last_pos(ast)
    if is_nullable(ast):
        automaton.final_states.add(0)
    
    # Construction des transitions
    # 1. Depuis l'état 0 vers les premières positions
    for first_pos_num in first_states:
        char = positions[first_pos_num]
        automaton.add_transition(0, char, first_pos_num)
    
    # 2. Entre les positions selon la table des successeurs
    for pos, succ_set in successors.items():
        if succ_set:  # Si la position a des successeurs
            for succ_pos in succ_set:
                char = positions[succ_pos]  # Le caractère de la position suivante
                automaton.add_transition(pos, char, succ_pos)
    
    return automaton, positions, successors

def construire_automate_glushkov(regex_str):
    """Interface pour construire un automate de Glushkov depuis une regex"""
    try:
        automaton, positions, successors = glushkov_correct(regex_str)
        
        # Recalculer pour le debug
        ast = parse_regex(regex_str)
        
        # Réassigner positions pour debug
        pos_counter = 1
        def reassign_positions(node):
            nonlocal pos_counter
            if node.kind == 'char':
                node.pos = pos_counter
                pos_counter += 1
            elif hasattr(node, 'left'):
                reassign_positions(node.left)
                if hasattr(node, 'right') and node.right:
                    reassign_positions(node.right)
        
        reassign_positions(ast)
        
        def first_pos_debug(node):
            if node.kind == 'char':
                return {node.pos}
            elif node.kind == 'union':
                return first_pos_debug(node.left) | first_pos_debug(node.right)
            elif node.kind == 'concat':
                if is_nullable_debug(node.left):
                    return first_pos_debug(node.left) | first_pos_debug(node.right)
                else:
                    return first_pos_debug(node.left)
            elif node.kind in ['star', 'plus']:
                return first_pos_debug(node.left)
            return set()
        
        def last_pos_debug(node):
            if node.kind == 'char':
                return {node.pos}
            elif node.kind == 'union':
                return last_pos_debug(node.left) | last_pos_debug(node.right)
            elif node.kind == 'concat':
                if is_nullable_debug(node.right):
                    return last_pos_debug(node.left) | last_pos_debug(node.right)
                else:
                    return last_pos_debug(node.right)
            elif node.kind in ['star', 'plus']:
                return last_pos_debug(node.left)
            return set()
        
        def is_nullable_debug(node):
            if node.kind == 'char':
                return False
            elif node.kind == 'union':
                return is_nullable_debug(node.left) or is_nullable_debug(node.right)
            elif node.kind == 'concat':
                return is_nullable_debug(node.left) and is_nullable_debug(node.right)
            elif node.kind == 'star':
                return True
            elif node.kind == 'plus':
                return False
            return False
        
        # Formatage des informations de debug
        debug_info = {
            'linearized': {f"pos_{k}": f"{v}_{k}" for k, v in positions.items()},
            'successors': {f"pos_{k}": [f"pos_{p}" for p in sorted(v)] if v else [] for k, v in successors.items()},
            'first_states': sorted(list(first_pos_debug(ast))),
            'last_states': sorted(list(last_pos_debug(ast))),
            'nullable': is_nullable_debug(ast)
        }
        
        return {
            'succes': True,
            'message': f'Automate de Glushkov construit pour "{regex_str}"',
            'automate': automaton.to_dict(),
            'debug': debug_info,
            'regex': regex_str
        }
    except Exception as e:
        return {
            'succes': False,
            'erreur': f'Erreur lors de la construction : {str(e)}'
        }

def debug_glushkov_construction(regex_str):
    """Affiche le processus de construction étape par étape"""
    print(f"=== Construction Glushkov pour: {regex_str} ===")
    
    try:
        automaton, positions, successors = glushkov_correct(regex_str)
        ast = parse_regex(regex_str)
        
        # Recalcul pour debug
        pos_counter = 1
        def reassign_for_debug(node):
            nonlocal pos_counter
            if node.kind == 'char':
                node.pos = pos_counter
                pos_counter += 1
            elif hasattr(node, 'left'):
                reassign_for_debug(node.left)
                if hasattr(node, 'right') and node.right:
                    reassign_for_debug(node.right)
        
        reassign_for_debug(ast)
        
        def first_pos_calc(node):
            if node.kind == 'char':
                return {node.pos}
            elif node.kind == 'union':
                return first_pos_calc(node.left) | first_pos_calc(node.right)
            elif node.kind == 'concat':
                if is_nullable_calc(node.left):
                    return first_pos_calc(node.left) | first_pos_calc(node.right)
                else:
                    return first_pos_calc(node.left)
            elif node.kind in ['star', 'plus']:
                return first_pos_calc(node.left)
            return set()
        
        def last_pos_calc(node):
            if node.kind == 'char':
                return {node.pos}
            elif node.kind == 'union':
                return last_pos_calc(node.left) | last_pos_calc(node.right)
            elif node.kind == 'concat':
                if is_nullable_calc(node.right):
                    return last_pos_calc(node.left) | last_pos_calc(node.right)
                else:
                    return last_pos_calc(node.right)
            elif node.kind in ['star', 'plus']:
                return last_pos_calc(node.left)
            return set()
        
        def is_nullable_calc(node):
            if node.kind == 'char':
                return False
            elif node.kind == 'union':
                return is_nullable_calc(node.left) or is_nullable_calc(node.right)
            elif node.kind == 'concat':
                return is_nullable_calc(node.left) and is_nullable_calc(node.right)
            elif node.kind == 'star':
                return True
            elif node.kind == 'plus':
                return False
            return False
        
        print(f"\n1. Linéarisation (positions attribuées):")
        for pos, char in sorted(positions.items()):
            print(f"   {char}_{pos}")
        
        print(f"\n2. Premières positions (First): {sorted(first_pos_calc(ast))}")
        print(f"3. Dernières positions (Last): {sorted(last_pos_calc(ast))}")
        print(f"4. Expression nullable: {is_nullable_calc(ast)}")
        
        print(f"\n5. Table des successeurs:")
        for pos in sorted(positions.keys()):
            char = positions[pos]
            succ_list = sorted(successors.get(pos, set()))
            if succ_list:
                succ_chars = [f'{positions[s]}_{s}' for s in succ_list]
                print(f"   {char}_{pos} → {succ_chars}")
            else:
                print(f"   {char}_{pos} → []")
        
        print(f"\n6. États finaux: {sorted(automaton.final_states)}")
        
        print(f"\n7. Transitions construites:")
        for (src, symbol), dests in sorted(automaton.transitions.items()):
            for dest in sorted(dests):
                print(f"   {src} --{symbol}--> {dest}")
        
        return automaton.to_dict()
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None
