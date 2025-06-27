from app.services.automaton_service import AutomatonService

class ConversionService:
    """Service pour les conversions d'automates"""
    
    @staticmethod
    def nfa_to_dfa(automaton_data):
        """Convertir AFN vers AFD"""
        from app.core.conversions.nfa_to_dfa import NFAToDFAConverter
        
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        converter = NFAToDFAConverter()
        dfa = converter.convert(automaton)
        
        return {
            'result': dfa.to_dict(),
            'steps': converter.get_conversion_steps()
        }
    
    @staticmethod
    def dfa_to_complete_dfa(automaton_data):
        """Convertir AFD vers AFDC"""
        from app.core.conversions.dfa_to_complete_dfa import DFAToCompleteDFAConverter
        
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        converter = DFAToCompleteDFAConverter()
        complete_dfa = converter.convert(automaton)
        
        return complete_dfa.to_dict()
    
    @staticmethod
    def epsilon_nfa_to_dfa(automaton_data):
        """Convertir epsilon-AFN vers AFD"""
        from app.core.conversions.epsilon_nfa_to_dfa import EpsilonNFAToDFAConverter
        
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        converter = EpsilonNFAToDFAConverter()
        dfa = converter.convert(automaton)
        
        return {
            'result': dfa.to_dict(),
            'epsilon_closures': converter.get_epsilon_closures()
        }
    
    @staticmethod
    def nfa_to_epsilon_nfa(automaton_data):
        """Convertir AFN vers epsilon-AFN"""
        from app.core.conversions.nfa_to_epsilon_nfa import NFAToEpsilonNFAConverter
        
        automaton = AutomatonService.create_automaton_from_dict(automaton_data)
        converter = NFAToEpsilonNFAConverter()
        epsilon_nfa = converter.convert(automaton)
        
        return epsilon_nfa.to_dict()
