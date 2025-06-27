class State:
    """Classe représentant un état d'automate"""
    
    def __init__(self, name, is_initial=False, is_final=False):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"State('{self.name}', initial={self.is_initial}, final={self.is_final})"
    
    def __eq__(self, other):
        return isinstance(other, State) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
