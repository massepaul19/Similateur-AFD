class Transition:
    """Classe représentant une transition d'automate"""
    
    def __init__(self, from_state, to_state, symbol):
        self.from_state = from_state
        self.to_state = to_state
        self.symbol = symbol  # Peut être 'ε' pour epsilon-transition
    
    def __str__(self):
        return f"{self.from_state} --{self.symbol}--> {self.to_state}"
    
    def __repr__(self):
        return f"Transition({self.from_state}, {self.to_state}, '{self.symbol}')"
    
    def is_epsilon(self):
        return self.symbol == 'ε' or self.symbol == 'epsilon'
