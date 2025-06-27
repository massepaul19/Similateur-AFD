import uuid
from collections import deque, defaultdict
from app.models.automate import db

class NFAToDFAConverter:
    """Convertisseur d'AFN vers AFD with step tracking"""
    
    def __init__(self, nfa_automate):
        self.nfa = nfa_automate
        self.nfa_states = {state.state_id: state for state in nfa_automate.states}
        self.nfa_transitions = self._build_transition_table()
        self.alphabet = set(nfa_automate.alphabet) - {'ε', ''}  # Retirer epsilon
        self.conversion_id = str(uuid.uuid4())
        self.conversion_steps = []
        self.step_counter = 0
        
        # Structures pour le DFA résultant
        self.dfa_states = {}
        self.dfa_transitions = []
        self.state_counter = 0
        self.state_name_mapping = {}  # {frozenset: 'q0', frozenset: 'q1', ...}
        
    def _build_transition_table(self):
        """Construit la table de transition de l'AFN"""
        table = defaultdict(lambda: defaultdict(list))
        
        for transition in self.nfa.transitions:
            from_state = transition.from_state
            symbol = transition.symbol
            to_state = transition.to_state
            table[from_state][symbol].append(to_state)
        
        return table
    
    def _add_step(self, step_type, description, current_state_set=None, symbol=None, 
                  result_state_set=None, details=None):
        """Ajoute une étape à la trace de conversion"""
        self.step_counter += 1
        
        step_data = {
            'conversion_id': self.conversion_id,
            'step_number': self.step_counter,
            'step_type': step_type,
            'description': description,
            'current_state_set': self._format_state_set(current_state_set) if current_state_set else None,
            'symbol': symbol,
            'result_state_set': self._format_state_set(result_state_set) if result_state_set else None,
            'details': details or {}
        }
        
        self.conversion_steps.append(step_data)
        return step_data
    
    def _format_state_set(self, state_set):
        """Formate un ensemble d'états pour l'affichage"""
        if not state_set:
            return None
        if isinstance(state_set, str):
            return state_set
        return '{' + ', '.join(sorted(state_set)) + '}'
    
    def epsilon_closure(self, states):
        """Calcule la fermeture epsilon d'un ensemble d'états"""
        if isinstance(states, str):
            states = {states}
        elif isinstance(states, list):
            states = set(states)
        
        closure = set(states)
        stack = list(states)
        
        self._add_step('epsilon_closure', 
                      f"Calcul de la fermeture epsilon de {self._format_state_set(states)}",
                      current_state_set=states,
                      details={'initial_states': list(states)})
        
        while stack:
            current = stack.pop()
            epsilon_transitions = self.nfa_transitions[current].get('ε', []) + \
                                self.nfa_transitions[current].get('', [])
            
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
                    
                    self._add_step('epsilon_transition',
                                  f"Transition epsilon: {current} → {next_state}",
                                  current_state_set=current,
                                  result_state_set=next_state,
                                  details={'transition_type': 'epsilon'})
        
        self._add_step('epsilon_closure_result',
                      f"Fermeture epsilon complète: {self._format_state_set(closure)}",
                      result_state_set=closure,
                      details={'closure_size': len(closure)})
        
        return frozenset(closure)
    
    def _get_state_name(self, state_set):
        """Obtient ou crée un nom pour un ensemble d'états"""
        if state_set not in self.state_name_mapping:
            self.state_name_mapping[state_set] = f"q{self.state_counter}"
            self.state_counter += 1
        return self.state_name_mapping[state_set]
    
    def _is_final_state(self, state_set):
        """Vérifie si un ensemble d'états contient un état final"""
        for state_id in state_set:
            if state_id in self.nfa_states and self.nfa_states[state_id].is_final:
                return True
        return False
    
    def convert(self):
        """Convertit l'AFN en AFD en utilisant la construction des sous-ensembles"""
        
        self._add_step('start', "Début de la conversion AFN → AFD", 
                      details={'nfa_states': len(self.nfa_states), 'alphabet': list(self.alphabet)})
        
        # 1. Trouver l'état initial du AFN
        initial_states = [state.state_id for state in self.nfa.states if state.is_initial]
        if not initial_states:
            raise ValueError("Aucun état initial trouvé dans l'AFN")
        
        # 2. Calculer la fermeture epsilon de l'état initial
        initial_closure = self.epsilon_closure(initial_states)
        initial_dfa_name = self._get_state_name(initial_closure)
        
        self._add_step('initial_state',
                      f"État initial du AFD: {initial_dfa_name} = {self._format_state_set(initial_closure)}",
                      result_state_set=initial_closure,
                      details={'dfa_state_name': initial_dfa_name})
        
        # Structures pour l'algorithme
        unprocessed = deque([initial_closure])
        processed = set()
        dfa_states = {initial_closure: {
            'name': initial_dfa_name,
            'is_initial': True,
            'is_final': self._is_final_state(initial_closure),
            'nfa_states': set(initial_closure)
        }}
        dfa_transitions = []
        
        # 3. Traiter chaque ensemble d'états
        while unprocessed:
            current_state_set = unprocessed.popleft()
            
            if current_state_set in processed:
                continue
                
            processed.add(current_state_set)
            current_name = dfa_states[current_state_set]['name']
            
            self._add_step('process_state',
                          f"Traitement de l'état {current_name} = {self._format_state_set(current_state_set)}",
                          current_state_set=current_state_set,
                          details={'state_name': current_name})
            
            # Pour chaque symbole de l'alphabet
            for symbol in self.alphabet:
                # Calculer l'ensemble des états atteignables
                next_states = set()
                
                for state in current_state_set:
                    transitions = self.nfa_transitions[state].get(symbol, [])
                    next_states.update(transitions)
                
                if not next_states:
                    self._add_step('no_transition',
                                  f"Aucune transition depuis {current_name} avec le symbole '{symbol}'",
                                  current_state_set=current_state_set,
                                  symbol=symbol)
                    continue
                
                # Calculer la fermeture epsilon
                next_closure = self.epsilon_closure(next_states)
                
                if next_closure not in dfa_states:
                    next_name = self._get_state_name(next_closure)
                    dfa_states[next_closure] = {
                        'name': next_name,
                        'is_initial': False,
                        'is_final': self._is_final_state(next_closure),
                        'nfa_states': set(next_closure)
                    }
                    unprocessed.append(next_closure)
                    
                    self._add_step('new_state',
                                  f"Nouvel état créé: {next_name} = {self._format_state_set(next_closure)}",
                                  result_state_set=next_closure,
                                  details={'state_name': next_name, 'is_final': self._is_final_state(next_closure)})
                
                next_name = dfa_states[next_closure]['name']
                
                # Ajouter la transition
                transition = {
                    'from_state': current_name,
                    'to_state': next_name,
                    'symbol': symbol
                }
                dfa_transitions.append(transition)
                
                self._add_step('transition',
                              f"Transition: {current_name} --{symbol}--> {next_name}",
                              current_state_set=current_state_set,
                              symbol=symbol,
                              result_state_set=next_closure,
                              details=transition)
        
        self._add_step('complete',
                      f"Conversion terminée. AFD avec {len(dfa_states)} états et {len(dfa_transitions)} transitions",
                      details={
                          'dfa_states_count': len(dfa_states),
                          'dfa_transitions_count': len(dfa_transitions),
                          'reduction_ratio': len(self.nfa_states) / len(dfa_states) if len(dfa_states) > 0 else 0
                      })
        
        # Préparer les résultats
        self.dfa_states = dfa_states
        self.dfa_transitions = dfa_transitions
        
        return self._build_dfa_result()
    
    def _build_dfa_result(self):
        """Construit le résultat de la conversion au format attendu"""
        # Calculer les positions des états (disposition circulaire)
        positions = self._calculate_positions(len(self.dfa_states))
        
        states_list = []
        transitions_list = []
        
        for i, (state_set, state_info) in enumerate(self.dfa_states.items()):
            states_list.append({
                'id': state_info['name'],
                'state_id': state_info['name'],
                'x': positions[i]['x'],
                'y': positions[i]['y'],
                'isInitial': state_info['is_initial'],
                'isFinal': state_info['is_final'],
                'is_initial': state_info['is_initial'],
                'is_final': state_info['is_final'],
                'nfa_states': list(state_info['nfa_states'])
            })
        
        for transition in self.dfa_transitions:
            transitions_list.append({
                'from_state': transition['from_state'],
                'to_state': transition['to_state'],
                'symbol': transition['symbol']
            })
        
        return {
            'name': f"AFD_de_{self.nfa.name}",
            'type': 'afd',
            'alphabet': list(self.alphabet),
            'states': states_list,
            'transitions': transitions_list,
            'initialState': next(state['name'] for state in self.dfa_states.values() if state['is_initial']),
            'conversion_steps': self.conversion_steps,
            'conversion_id': self.conversion_id,
            'original_nfa_id': self.nfa.id
        }
    
    def _calculate_positions(self, num_states):
        """Calcule les positions des états pour l'affichage"""
        import math
        
        positions = []
        if num_states == 1:
            positions.append({'x': 200, 'y': 150})
        else:
            center_x, center_y = 200, 150
            radius = min(120, 30 + num_states * 10)
            
            for i in range(num_states):
                angle = 2 * math.pi * i / num_states - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append({'x': x, 'y': y})
        
        return positions
    
    def save_conversion_steps(self):
        """Sauvegarde les étapes de conversion en base de données"""
        try:
            from models import ConversionStep
            
            for step_data in self.conversion_steps:
                step = ConversionStep(
                    conversion_id=step_data['conversion_id'],
                    step_number=step_data['step_number'],
                    step_type=step_data['step_type'],
                    description=step_data['description'],
                    current_state_set=step_data['current_state_set'],
                    symbol=step_data['symbol'],
                    result_state_set=step_data['result_state_set'],
                    details=step_data['details']
                )
                db.session.add(step)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde des étapes: {e}")
            return False

