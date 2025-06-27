from app.models import Automaton, RegularExpression

class ValidationService:
    """Service pour la validation des données"""
    
    @staticmethod
    def validate_automaton_data(data):
        """Valider les données d'un automate"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Les données doivent être un objet JSON")
            return errors
        
        # Vérifier la présence des champs requis
        required_fields = ['states', 'transitions']
        for field in required_fields:
            if field not in data:
                errors.append(f"Champ requis manquant: {field}")
        
        # Valider les états
        if 'states' in data:
            if not isinstance(data['states'], list):
                errors.append("Le champ 'states' doit être une liste")
            else:
                state_names = set()
                has_initial = False
                
                for i, state in enumerate(data['states']):
                    if not isinstance(state, dict):
                        errors.append(f"L'état {i} doit être un objet")
                        continue
                    
                    if 'name' not in state:
                        errors.append(f"L'état {i} doit avoir un nom")
                        continue
                    
                    if state['name'] in state_names:
                        errors.append(f"Nom d'état dupliqué: {state['name']}")
                    
                    state_names.add(state['name'])
                    
                    if state.get('initial', False):
                        has_initial = True
                
                if not has_initial and data['states']:
                    errors.append("Au moins un état initial doit être défini")
        
        # Valider les transitions
        if 'transitions' in data and 'states' in data:
            state_names = {state['name'] for state in data['states']}
            
            for i, transition in enumerate(data['transitions']):
                if not isinstance(transition, dict):
                    errors.append(f"La transition {i} doit être un objet")
                    continue
                
                required_trans_fields = ['from', 'to', 'symbol']
                for field in required_trans_fields:
                    if field not in transition:
                        errors.append(f"La transition {i} doit avoir le champ '{field}'")
                
                if transition.get('from') not in state_names:
                    errors.append(f"État source invalide dans la transition {i}: {transition.get('from')}")
                
                if transition.get('to') not in state_names:
                    errors.append(f"État destination invalide dans la transition {i}: {transition.get('to')}")
        
        return errors
    
    @staticmethod
    def validate_regex(pattern):
        """Valider une expression régulière"""
        errors = []
        
        if not isinstance(pattern, str):
            errors.append("L'expression régulière doit être une chaîne de caractères")
            return errors
        
        if not pattern.strip():
            errors.append("L'expression régulière ne peut pas être vide")
            return errors
        
        # Vérification basique de la syntaxe
        stack = []
        for i, char in enumerate(pattern):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    errors.append(f"Parenthèse fermante non appariée à la position {i}")
                else:
                    stack.pop()
        
        if stack:
            errors.append(f"Parenthèse ouvrante non appariée à la position {stack[-1]}")
        
        return errors
