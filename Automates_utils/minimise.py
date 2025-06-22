# minimise.py - Minimisation d'automates finis déterministes
from collections import defaultdict, deque

class MinimisationAutomate:
    """Classe pour la minimisation d'automates finis déterministes"""
    
    def __init__(self, automate):
        """
        Initialise avec un automate au format dictionnaire
        Format attendu:
        {
            'alphabet': ['a', 'b', ...],
            'etats': ['q0', 'q1', ...],
            'etats_initiaux': ['q0'],
            'etats_finaux': ['q2', ...],
            'transitions': {'q0,a': ['q1'], 'q1,b': ['q2'], ...}
        }
        """
        self.alphabet = automate.get('alphabet', [])
        self.etats = set(automate.get('etats', []))
        self.etats_initiaux = set(automate.get('etats_initiaux', []))
        self.etats_finaux = set(automate.get('etats_finaux', []))
        self.transitions = automate.get('transitions', {})
        
        # Convertir les transitions en dictionnaire plus pratique
        self.delta = {}
        for cle, destinations in self.transitions.items():
            if ',' in cle:
                etat, symbole = cle.split(',', 1)
                if destinations:  # Si il y a des destinations
                    self.delta[(etat, symbole)] = destinations[0]  # AFD: une seule destination
    
    def supprimer_etats_inaccessibles(self):
        """Supprime les états inaccessibles depuis les états initiaux"""
        if not self.etats_initiaux:
            return set(), set()
        
        # Parcours en largeur pour trouver tous les états accessibles
        accessibles = set()
        file = deque(self.etats_initiaux)
        accessibles.update(self.etats_initiaux)
        
        while file:
            etat_courant = file.popleft()
            
            # Explorer toutes les transitions depuis cet état
            for symbole in self.alphabet:
                if (etat_courant, symbole) in self.delta:
                    etat_suivant = self.delta[(etat_courant, symbole)]
                    if etat_suivant not in accessibles:
                        accessibles.add(etat_suivant)
                        file.append(etat_suivant)
        
        inaccessibles = self.etats - accessibles
        
        # Mettre à jour l'automate
        self.etats = accessibles
        self.etats_finaux = self.etats_finaux & accessibles
        
        # Supprimer les transitions impliquant des états inaccessibles
        nouvelles_transitions = {}
        for (etat, symbole), destination in self.delta.items():
            if etat in accessibles and destination in accessibles:
                nouvelles_transitions[(etat, symbole)] = destination
        self.delta = nouvelles_transitions
        
        return accessibles, inaccessibles
    
    def construire_table_distinguabilite(self):
        """Construit la table de distinguabilité pour identifier les états équivalents"""
        etats_liste = list(self.etats)
        n = len(etats_liste)
        
        # Table de distinguabilité (matrice triangulaire supérieure)
        distinguable = {}
        
        # Initialisation: marquer les paires (final, non-final) comme distinguables
        for i in range(n):
            for j in range(i + 1, n):
                etat1, etat2 = etats_liste[i], etats_liste[j]
                # Deux états sont distinguables s'ils ont des caractères de finalité différents
                if (etat1 in self.etats_finaux) != (etat2 in self.etats_finaux):
                    distinguable[(etat1, etat2)] = True
                else:
                    distinguable[(etat1, etat2)] = False
        
        # Algorithme itératif pour propager la distinguabilité
        changement = True
        while changement:
            changement = False
            
            for i in range(n):
                for j in range(i + 1, n):
                    etat1, etat2 = etats_liste[i], etats_liste[j]
                    
                    if not distinguable.get((etat1, etat2), False):
                        # Vérifier si les états sont distinguables par leurs transitions
                        for symbole in self.alphabet:
                            dest1 = self.delta.get((etat1, symbole))
                            dest2 = self.delta.get((etat2, symbole))
                            
                            # Si les destinations sont différentes et distinguables
                            if dest1 != dest2:
                                if dest1 is None or dest2 is None:
                                    # L'un a une transition, l'autre non
                                    distinguable[(etat1, etat2)] = True
                                    changement = True
                                    break
                                else:
                                    # Ordonner pour accéder à la table
                                    if dest1 > dest2:
                                        dest1, dest2 = dest2, dest1
                                    
                                    if distinguable.get((dest1, dest2), False):
                                        distinguable[(etat1, etat2)] = True
                                        changement = True
                                        break
        
        return distinguable
    
    def regrouper_etats_equivalents(self, table_distinguabilite):
        """Regroupe les états équivalents en classes d'équivalence"""
        etats_liste = list(self.etats)
        n = len(etats_liste)
        
        # Union-Find pour regrouper les états équivalents
        parent = {etat: etat for etat in self.etats}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Regrouper les états non-distinguables
        for i in range(n):
            for j in range(i + 1, n):
                etat1, etat2 = etats_liste[i], etats_liste[j]
                if not table_distinguabilite.get((etat1, etat2), False):
                    union(etat1, etat2)
        
        # Construire les classes d'équivalence
        classes = defaultdict(list)
        for etat in self.etats:
            representant = find(etat)
            classes[representant].append(etat)
        
        return dict(classes)
    
    def construire_automate_minimise(self, classes_equivalence):
        """Construit l'automate minimisé à partir des classes d'équivalence"""
        # Mapping des anciens états vers leurs représentants de classe
        etat_vers_classe = {}
        nouveaux_etats = []
        
        for representant, membres in classes_equivalence.items():
            # Le nom de la nouvelle classe est la liste triée des membres
            nom_classe = '{' + ','.join(sorted(membres)) + '}'
            nouveaux_etats.append(nom_classe)
            
            for membre in membres:
                etat_vers_classe[membre] = nom_classe
        
        # Nouveaux états initiaux
        nouveaux_etats_initiaux = []
        for etat_initial in self.etats_initiaux:
            classe = etat_vers_classe[etat_initial]
            if classe not in nouveaux_etats_initiaux:
                nouveaux_etats_initiaux.append(classe)
        
        # Nouveaux états finaux
        nouveaux_etats_finaux = []
        for etat_final in self.etats_finaux:
            classe = etat_vers_classe[etat_final]
            if classe not in nouveaux_etats_finaux:
                nouveaux_etats_finaux.append(classe)
        
        # Nouvelles transitions
        nouvelles_transitions = {}
        for (etat, symbole), destination in self.delta.items():
            classe_source = etat_vers_classe[etat]
            classe_dest = etat_vers_classe[destination]
            
            cle = f"{classe_source},{symbole}"
            if cle not in nouvelles_transitions:
                nouvelles_transitions[cle] = [classe_dest]
        
        return {
            'alphabet': self.alphabet,
            'etats': nouveaux_etats,
            'etats_initiaux': nouveaux_etats_initiaux,
            'etats_finaux': nouveaux_etats_finaux,
            'transitions': nouvelles_transitions
        }
    
    def minimiser(self):
        """
        Minimise l'automate complet
        Retourne: (automate_minimise, informations_debug)
        """
        # Étape 1: Supprimer les états inaccessibles
        accessibles, inaccessibles = self.supprimer_etats_inaccessibles()
        
        # Étape 2: Construire la table de distinguabilité
        table_distinguabilite = self.construire_table_distinguabilite()
        
        # Étape 3: Regrouper les états équivalents
        classes_equivalence = self.regrouper_etats_equivalents(table_distinguabilite)
        
        # Étape 4: Construire l'automate minimisé
        automate_minimise = self.construire_automate_minimise(classes_equivalence)
        
        # Informations pour le debug
        info_debug = {
            'etats_inaccessibles': list(inaccessibles),
            'etats_accessibles': list(accessibles),
            'classes_equivalence': {rep: membres for rep, membres in classes_equivalence.items()},
            'nombre_etats_original': len(self.etats) + len(inaccessibles),
            'nombre_etats_minimise': len(automate_minimise['etats'])
        }
        
        return automate_minimise, info_debug


def minimiser_automate(automate):
    """
    Fonction utilitaire pour minimiser un automate
    
    Args:
        automate: Dictionnaire représentant l'automate
        
    Returns:
        tuple: (automate_minimise, informations_debug)
    """
    minimiseur = MinimisationAutomate(automate)
    return minimiseur.minimiser()


# Fonction de test
def test_minimisation():
    """Test de la minimisation avec un exemple simple"""
    automate_test = {
        'alphabet': ['a', 'b'],
        'etats': ['q0', 'q1', 'q2', 'q3', 'q4'],
        'etats_initiaux': ['q0'],
        'etats_finaux': ['q2', 'q4'],
        'transitions': {
            'q0,a': ['q1'],
            'q0,b': ['q2'],
            'q1,a': ['q0'],
            'q1,b': ['q3'],
            'q2,a': ['q4'],
            'q2,b': ['q0'],
            'q3,a': ['q2'],
            'q3,b': ['q1'],
            'q4,a': ['q3'],
            'q4,b': ['q4']
        }
    }
    
    automate_min, info = minimiser_automate(automate_test)
    
    print("=== Test de minimisation ===")
    print(f"États originaux: {automate_test['etats']}")
    print(f"États minimisés: {automate_min['etats']}")
    print(f"Classes d'équivalence: {info['classes_equivalence']}")
    print(f"Réduction: {info['nombre_etats_original']} → {info['nombre_etats_minimise']} états")


if __name__ == "__main__":
    test_minimisation()
