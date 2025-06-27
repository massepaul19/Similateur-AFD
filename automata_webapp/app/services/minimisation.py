from collections import defaultdict, deque
from itertools import combinations
from app.models.automate import Automate, AutomateState, AutomateTransition, AutomateService, db

class MinimizationService:
    
    @staticmethod
    def minimize_automate(automate_id):
        """
        Minimise un automate fini déterministe complet (AFDC)
        Utilise l'algorithme de Moore pour la minimisation
        """
        automate = AutomateService.get_automate(automate_id)
        
        if automate.type != 'afdc':
            raise ValueError("Seuls les AFDC peuvent être minimisés avec cette méthode")
        
        # Étape 1: Construire la table de transitions
        states = {state.state_id for state in automate.states}
        alphabet = set(automate.alphabet)
        transitions = {}
        
        for transition in automate.transitions:
            key = (transition.from_state, transition.symbol)
            transitions[key] = transition.to_state
        
        # Étape 2: Identifier les états finaux et non-finaux
        final_states = {state.state_id for state in automate.states if state.is_final}
        non_final_states = states - final_states
        
        # Étape 3: Algorithme de Moore - Partition initiale
        partitions = []
        if non_final_states:
            partitions.append(list(non_final_states))
        if final_states:
            partitions.append(list(final_states))
        
        steps = [{'step': 0, 'partitions': [p.copy() for p in partitions], 'description': 'Partition initiale (états finaux/non-finaux)'}]
        
        changed = True
        step_num = 1
        
        while changed:
            changed = False
            new_partitions = []
            
            for partition in partitions:
                if len(partition) <= 1:
                    new_partitions.append(partition)
                    continue
                
                # Grouper les états selon leurs transitions
                groups = defaultdict(list)
                
                for state in partition:
                    signature = []
                    for symbol in sorted(alphabet):
                        target = transitions.get((state, symbol))
                        # Trouver dans quelle partition se trouve l'état cible
                        target_partition = -1
                        for i, p in enumerate(partitions):
                            if target in p:
                                target_partition = i
                                break
                        signature.append(target_partition)
                    
                    groups[tuple(signature)].append(state)
                
                # Si on a plus d'un groupe, on divise la partition
                if len(groups) > 1:
                    changed = True
                    for group in groups.values():
                        new_partitions.append(group)
                else:
                    new_partitions.append(partition)
            
            partitions = new_partitions
            if changed:
                steps.append({
                    'step': step_num,
                    'partitions': [p.copy() for p in partitions],
                    'description': f'Étape {step_num}: Raffinage des partitions'
                })
                step_num += 1
        
        # Étape 4: Construire l'automate minimisé
        minimized_data = MinimizationService._build_minimized_automate(
            automate, partitions, transitions, alphabet
        )
        
        return {
            'original': automate.to_dict(),
            'minimized': minimized_data,
            'steps': steps,
            'reduction': {
                'original_states': len(states),
                'minimized_states': len(partitions),
                'reduction_percentage': round((1 - len(partitions) / len(states)) * 100, 1)
            }
        }
    
    @staticmethod
    def _build_minimized_automate(automate, partitions, transitions, alphabet):
        """Construit l'automate minimisé à partir des partitions"""
        
        # Créer un mapping état -> partition
        state_to_partition = {}
        partition_names = {}
        
        for i, partition in enumerate(partitions):
            partition_name = f"q{i}"
            partition_names[i] = partition_name
            for state in partition:
                state_to_partition[state] = i
        
        # États du nouveau automate
        minimized_states = []
        for i, partition in enumerate(partitions):
            # Vérifier si c'est un état initial
            is_initial = automate.initial_state in partition
            # Vérifier si c'est un état final
            is_final = any(state.is_final for state in automate.states if state.state_id in partition)
            
            minimized_states.append({
                'id': partition_names[i],
                'x': 100 + (i % 4) * 150,  # Position pour visualisation
                'y': 100 + (i // 4) * 100,
                'isInitial': is_initial,
                'isFinal': is_final,
                'originalStates': partition
            })
        
        # Transitions du nouveau automate
        minimized_transitions = []
        transition_set = set()
        
        for (from_state, symbol), to_state in transitions.items():
            from_partition = state_to_partition[from_state]
            to_partition = state_to_partition[to_state]
            
            transition_key = (from_partition, symbol, to_partition)
            if transition_key not in transition_set:
                transition_set.add(transition_key)
                minimized_transitions.append([
                    f"{partition_names[from_partition]},{symbol}",
                    [partition_names[to_partition]]
                ])
        
        return {
            'name': f"{automate.name} (minimisé)",
            'description': f"Version minimisée de {automate.name}",
            'type': 'afdc',
            'alphabet': list(alphabet),
            'initialState': next(partition_names[i] for i, partition in enumerate(partitions) 
                                if automate.initial_state in partition),
            'states': minimized_states,
            'transitions': minimized_transitions
        }
    
    @staticmethod
    def check_equivalence(automate1_id, automate2_id):
        """Vérifie si deux automates sont équivalents"""
        # Cette méthode pourrait être implémentée pour comparer deux automates
        # en utilisant l'algorithme de minimisation ou d'autres techniques
        pass
    
    @staticmethod
    def get_distinguishing_sequences(automate_id):
        """
        Génère les séquences distinguantes pour un automate
        Utile pour la validation de la minimisation
        """
        automate = AutomateService.get_automate(automate_id)
        
        if automate.type != 'afdc':
            return None
        
        states = {state.state_id for state in automate.states}
        alphabet = set(automate.alphabet)
        transitions = {}
        
        for transition in automate.transitions:
            key = (transition.from_state, transition.symbol)
            transitions[key] = transition.to_state
        
        final_states = {state.state_id for state in automate.states if state.is_final}
        
        # Table de distinguabilité
        distinguishable = {}
        sequences = {}
        
        # Initialiser avec les paires d'états finaux/non-finaux
        for s1 in states:
            for s2 in states:
                if s1 < s2:  # Éviter les doublons
                    if (s1 in final_states) != (s2 in final_states):
                        distinguishable[(s1, s2)] = True
                        sequences[(s1, s2)] = ""  # Séquence vide distingue
                    else:
                        distinguishable[(s1, s2)] = False
        
        # Algorithme itératif pour trouver les séquences distinguantes
        changed = True
        while changed:
            changed = False
            for (s1, s2), is_dist in list(distinguishable.items()):
                if not is_dist:
                    for symbol in alphabet:
                        t1 = transitions.get((s1, symbol))
                        t2 = transitions.get((s2, symbol))
                        
                        if t1 and t2 and t1 != t2:
                            pair_key = (min(t1, t2), max(t1, t2))
                            if pair_key in distinguishable and distinguishable[pair_key]:
                                distinguishable[(s1, s2)] = True
                                base_seq = sequences.get(pair_key, "")
                                sequences[(s1, s2)] = symbol + base_seq
                                changed = True
                                break
        
        return {
            'distinguishable_pairs': {f"{s1},{s2}": seq for (s1, s2), seq in sequences.items() 
                                    if distinguishable.get((s1, s2), False)},
            'equivalent_pairs': [f"{s1},{s2}" for (s1, s2), is_dist in distinguishable.items() 
                               if not is_dist]
        }
