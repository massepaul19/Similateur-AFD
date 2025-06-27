class RegularExpression:
    """Classe pour représenter une expression régulière"""
    
    def __init__(self, pattern=""):
        self.pattern = pattern
        self.parsed_tree = None
    
    def __str__(self):
        return self.pattern
    
    def is_valid(self):
        """Vérifier si l'expression régulière est valide"""
        # TODO: Implémenter la validation
        return True
    
    def get_alphabet(self):
        """Extraire l'alphabet de l'expression régulière"""
        # TODO: Implémenter l'extraction de l'alphabet
        alphabet = set()
        for char in self.pattern:
            if char.isalnum():
                alphabet.add(char)
        return alphabet
