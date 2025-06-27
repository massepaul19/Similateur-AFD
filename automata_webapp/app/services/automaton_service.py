from app.models import Automaton, State, Transition
from app.core.conversions import *
from app.core.operations import *
from app.core.algorithms import *

class AutomatonService:
    """Service principal pour les opérations sur les automates"""
    
    @staticmethod
    def create_automaton_from_dict(data):
        """Créer un automate à partir d'un dictionnaire"""
        automaton = Automaton(data.get('name', ''))
        
        # Créer les états
        states_map = {}
        for state_data in data.get('states', []):
            state = State(
                name=state_data['name'],
                is_initial=state_data.get('initial', False),
                is_final=state_data.get('final', False)
            )
            automaton.add_state(state)
            states_map[state.name] = state
        
        # Créer les transitions
        for trans_data in data.get('transitions', []):
            from_state = states_map[trans_data['from']]
            to_state = states_map[trans_data['to']]
            symbol = trans_data['symbol']
            
            transition = Transition(from_state, to_state, symbol)
            automaton.add_transition(transition)
        
        return automaton
    
    @staticmethod
    def analyze_states(automaton_data):
        """Analyser les états d'un automate"""
        from app.core.operations.state_analysis import StateAnalyzer
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        
        analyzer = StateAnalyzer(automaton)
        return {
            'accessible_states': [s.name for s in analyzer.get_accessible_states()],
            'coaccessible_states': [s.name for s in analyzer.get_coaccessible_states()],
            'useful_states': [s.name for s in analyzer.get_useful_states()]
        }
    
    @staticmethod
    def minimize_automaton(automaton_data):
        """Minimiser un automate"""
        from app.core.operations.minimization import AutomatonMinimizer
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        
        minimizer = AutomatonMinimizer()
        minimized = minimizer.minimize(automaton)
        return minimized.to_dict()
    
    @staticmethod
    def prune_automaton(automaton_data):
        """Émonder un automate"""
        from app.core.operations.pruning import AutomatonPruner
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        
        pruner = AutomatonPruner()
        pruned = pruner.prune(automaton)
        return pruned.to_dict()
    
    @staticmethod
    def thompson_construction(regex_pattern):
        """Construction de Thompson"""
        from app.core.algorithms.thompson import ThompsonConstructor
        constructor = ThompsonConstructor()
        automaton = constructor.construct(regex_pattern)
        return automaton.to_dict()
    
    @staticmethod
    def glushkov_construction(regex_pattern):
        """Algorithme de Glushkov"""
        from app.core.algorithms.glushkov import GlushkovConstructor
        constructor = GlushkovConstructor()
        automaton = constructor.construct(regex_pattern)
        return automaton.to_dict()
    
    @staticmethod
    def extract_regex(automaton_data):
        """Extraire une expression régulière d'un automate"""
        from app.core.expressions.regex_generator import RegexGenerator
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        
        generator = RegexGenerator()
        regex = generator.generate(automaton)
        return {'regex': str(regex)}
    
    @staticmethod
    def solve_equation_system(equations):
        """Résoudre un système d'équations"""
        from app.core.algorithms.system_solver import SystemSolver
        solver = SystemSolver()
        result = solver.solve(equations)
        return result
    
    @staticmethod
    def perform_closure_operation(operation, automata_data):
        """Effectuer une opération de clôture"""
        from app.core.operations.closure_operations import ClosureOperations
        
        automata = [AutomatonService.create_automaton_from_dict(data) for data in automata_data]
        ops = ClosureOperations()
        
        if operation == 'union':
            result = ops.union(automata[0], automata[1])
        elif operation == 'intersection':
            result = ops.intersection(automata[0], automata[1])
        elif operation == 'complement':
            result = ops.complement(automata[0])
        elif operation == 'concatenation':
            result = ops.concatenation(automata[0], automata[1])
        else:
            raise ValueError(f"Opération non supportée: {operation}")
        
        return result.to_dict()

