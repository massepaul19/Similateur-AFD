from typing import Set, Dict, List
from .state import State
from .transition import Transition

class Automaton:
    """Classe de base pour représenter un automate"""
    
    def __init__(self, name=""):
        self.name = name
        self.states: Set[State] = set()
        self.alphabet: Set[str] = set()
        self.transitions: List[Transition] = []
        self.initial_states: Set[State] = set()
        self.final_states: Set[State] = set()
        self.transition_table: Dict = {}
    
    def add_state(self, state: State):
        """Ajouter un état à l'automate"""
        self.states.add(state)
        if state.is_initial:
            self.initial_states.add(state)
        if state.is_final:
            self.final_states.add(state)
    
    def add_transition(self, transition: Transition):
        """Ajouter une transition à l'automate"""
        self.transitions.append(transition)
        if not transition.is_epsilon():
            self.alphabet.add(transition.symbol)
        
        # Mise à jour de la table de transition
        key = (transition.from_state, transition.symbol)
        if key not in self.transition_table:
            self.transition_table[key] = set()
        self.transition_table[key].add(transition.to_state)
    
    def get_transitions_from(self, state: State, symbol: str = None):
        """Obtenir les transitions depuis un état donné"""
        if symbol:
            key = (state, symbol)
            return self.transition_table.get(key, set())
        else:
            result = []
            for transition in self.transitions:
                if transition.from_state == state:
                    result.append(transition)
            return result
    
    def is_deterministic(self):
        """Vérifier si l'automate est déterministe"""
        if len(self.initial_states) > 1:
            return False
        
        for state in self.states:
            for symbol in self.alphabet:
                transitions = self.get_transitions_from(state, symbol)
                if len(transitions) > 1:
                    return False
        return True
    
    def has_epsilon_transitions(self):
        """Vérifier si l'automate a des epsilon-transitions"""
        return any(t.is_epsilon() for t in self.transitions)
    
    def to_dict(self):
        """Convertir l'automate en dictionnaire pour la sérialisation"""
        return {
            'name': self.name,
            'states': [{'name': s.name, 'initial': s.is_initial, 'final': s.is_final} 
                      for s in self.states],
            'alphabet': list(self.alphabet),
            'transitions': [{'from': t.from_state.name, 'to': t.to_state.name, 'symbol': t.symbol} 
                           for t in self.transitions]
        }
