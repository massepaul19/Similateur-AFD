class Automate:
    def __init__(self, alphabet, etats, transitions, initial, final):
        self.alphabet = alphabet
        self.etats = etats
        self.transitions = transitions
        self.etat_initial = initial
        self.etats_final = final
    
    def afficher_automate(self):
        print(f"Alphabet: {self.alphabet}")
        print(f"États: {self.etats}")
        print(f"État initial: {self.etat_initial}")
        print(f"États finaux: {self.etats_final}")
        print("Transitions:")
        for etat, trans in self.transitions.items():
            for symbole, destinations in trans.items():
                if isinstance(destinations, list):
                    for dest in destinations:
                        print(f"  {etat} --{symbole}--> {dest}")
                else:
                    print(f"  {etat} --{symbole}--> {destinations}")
        print()
    
    def convertir_afn_en_afd(self):
        """Convertit un AFN en AFD en utilisant l'algorithme de construction de sous-ensembles"""
        
        # Nouvelle structure pour l'AFD
        nouveaux_etats = []
        nouvelles_transitions = {}
        nouveaux_finaux = []
        
        # File d'attente pour traiter les nouveaux états
        queue = []
        traites = set()
        
        # État initial de l'AFD (ensemble contenant l'état initial de l'AFN)
        etat_initial_afd = frozenset(self.etat_initial)
        queue.append(etat_initial_afd)
        nouveaux_etats.append(etat_initial_afd)
        
        while queue:
            etat_courant = queue.pop(0)
            
            if etat_courant in traites:
                continue
            traites.add(etat_courant)
            
            # Pour chaque symbole de l'alphabet
            for symbole in self.alphabet:
                # Calculer l'ensemble des états atteignables
                nouvel_etat = set()
                
                for etat in etat_courant:
                    if etat in self.transitions and symbole in self.transitions[etat]:
                        destinations = self.transitions[etat][symbole]
                        if isinstance(destinations, list):
                            nouvel_etat.update(destinations)
                        else:
                            nouvel_etat.add(destinations)
                
                if nouvel_etat:  # Si l'ensemble n'est pas vide
                    nouvel_etat_frozen = frozenset(nouvel_etat)
                    
                    # Ajouter la transition
                    if etat_courant not in nouvelles_transitions:
                        nouvelles_transitions[etat_courant] = {}
                    nouvelles_transitions[etat_courant][symbole] = nouvel_etat_frozen
                    
                    # Ajouter le nouvel état s'il n'existe pas déjà
                    if nouvel_etat_frozen not in nouveaux_etats:
                        nouveaux_etats.append(nouvel_etat_frozen)
                        queue.append(nouvel_etat_frozen)
        
        # Déterminer les états finaux de l'AFD
        for etat in nouveaux_etats:
            if any(e in self.etats_final for e in etat):
                nouveaux_finaux.append(etat)
        
        # Créer l'AFD résultant
        # Convertir les frozensets en chaînes pour l'affichage
        etats_str = ['{' + ','.join(sorted(etat)) + '}' for etat in nouveaux_etats]
        transitions_str = {}
        
        for etat, trans in nouvelles_transitions.items():
            etat_str = '{' + ','.join(sorted(etat)) + '}'
            transitions_str[etat_str] = {}
            for symbole, dest in trans.items():
                dest_str = '{' + ','.join(sorted(dest)) + '}'
                transitions_str[etat_str][symbole] = dest_str
        
        initial_str = ['{' + ','.join(sorted(etat_initial_afd)) + '}']
        finaux_str = ['{' + ','.join(sorted(etat)) + '}' for etat in nouveaux_finaux]
        
        return Automate(self.alphabet, etats_str, transitions_str, initial_str, finaux_str)


# Exemple d'utilisation avec votre AFN corrigé
alphabet = ['a', 'b']
etats = ['1', '2', '3', '4']

# Correction de la structure des transitions (AFN peut avoir plusieurs destinations)
transitions = {
    '1': {'a': ['1', '2']}, 
    '2': {'a': ['4'], 'b': ['3']},
    '3': {'b': ['3', '4']},     
}

etat_initial = ['1']
etats_finaux = ['4']

# Création de l'AFN
afn = Automate(alphabet, etats, transitions, etat_initial, etats_finaux)

print("=== AUTOMATE FINI NON-DÉTERMINISTE (AFN) ===")
afn.afficher_automate()

# Conversion en AFD
afd = afn.convertir_afn_en_afd()

print("=== AUTOMATE FINI DÉTERMINISTE (AFD) ===")
afd.afficher_automate()

# Test d'acceptation d'un mot
def tester_mot(automate, mot):
    """Teste si un mot est accepté par l'automate (version AFD)"""
    etat_courant = automate.etat_initial[0]
    
    for symbole in mot:
        if etat_courant in automate.transitions and symbole in automate.transitions[etat_courant]:
            etat_courant = automate.transitions[etat_courant][symbole]
        else:
            return False
    
    return etat_courant in automate.etats_final

# Tests
mots_test = ['a', 'aa', 'aba', 'abb', 'aab', 'aabb']
print("=== TESTS D'ACCEPTATION ===")
for mot in mots_test:
    resultat = tester_mot(afd, mot)
    print(f"Mot '{mot}': {'Accepté' if resultat else 'Rejeté'}")