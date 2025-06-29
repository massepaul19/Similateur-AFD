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
            if ',' in cle and destinations:  # Vérifier que destinations n'est pas vide
                parts = cle.split(',', 1)
                if len(parts) == 2:
                    etat, symbole = parts
                    # AFD: une seule destination
                    self.delta[(etat, symbole)] = destinations[0]
    
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
                    if etat_suivant not in accessibles and etat_suivant in self.etats:
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
        etats_liste = sorted(list(self.etats))  # Tri pour consistance
        n = len(etats_liste)
        
        # Table de distinguabilité
        distinguable = {}
        
        # Initialisation: marquer les paires (final, non-final) comme distinguables
        for i in range(n):
            for j in range(i + 1, n):
                etat1, etat2 = etats_liste[i], etats_liste[j]
                cle = (etat1, etat2) if etat1 < etat2 else (etat2, etat1)
                
                # Deux états sont distinguables s'ils ont des caractères de finalité différents
                if (etat1 in self.etats_finaux) != (etat2 in self.etats_finaux):
                    distinguable[cle] = True
                else:
                    distinguable[cle] = False
        
        # Algorithme itératif pour propager la distinguabilité
        changement = True
        iterations = 0
        max_iterations = n * n  # Éviter les boucles infinies
        
        while changement and iterations < max_iterations:
            changement = False
            iterations += 1
            
            for i in range(n):
                for j in range(i + 1, n):
                    etat1, etat2 = etats_liste[i], etats_liste[j]
                    cle = (etat1, etat2) if etat1 < etat2 else (etat2, etat1)
                    
                    if not distinguable.get(cle, False):
                        # Vérifier si les états sont distinguables par leurs transitions
                        for symbole in self.alphabet:
                            dest1 = self.delta.get((etat1, symbole))
                            dest2 = self.delta.get((etat2, symbole))
                            
                            # Cas où les destinations sont différentes
                            if dest1 != dest2:
                                # Si l'un a une transition et l'autre non
                                if dest1 is None or dest2 is None:
                                    distinguable[cle] = True
                                    changement = True
                                    break
                                # Si les deux ont des transitions vers des états différents
                                elif dest1 != dest2:
                                    # Vérifier si les destinations sont distinguables
                                    cle_dest = (dest1, dest2) if dest1 < dest2 else (dest2, dest1)
                                    if distinguable.get(cle_dest, False):
                                        distinguable[cle] = True
                                        changement = True
                                        break
        
        return distinguable
    
    def regrouper_etats_equivalents(self, table_distinguabilite):
        """Regroupe les états équivalents en classes d'équivalence"""
        etats_liste = sorted(list(self.etats))
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
                cle = (etat1, etat2) if etat1 < etat2 else (etat2, etat1)
                if not table_distinguabilite.get(cle, False):
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
            # Le nom de la nouvelle classe - utiliser le premier état trié comme nom
            membres_tries = sorted(membres)
            if len(membres_tries) == 1:
                nom_classe = membres_tries[0]
            else:
                nom_classe = '{' + ','.join(membres_tries) + '}'
            
            nouveaux_etats.append(nom_classe)
            
            for membre in membres:
                etat_vers_classe[membre] = nom_classe
        
        # Nouveaux états initiaux
        nouveaux_etats_initiaux = []
        for etat_initial in self.etats_initiaux:
            classe = etat_vers_classe.get(etat_initial)
            if classe and classe not in nouveaux_etats_initiaux:
                nouveaux_etats_initiaux.append(classe)
        
        # Nouveaux états finaux
        nouveaux_etats_finaux = []
        for etat_final in self.etats_finaux:
            classe = etat_vers_classe.get(etat_final)
            if classe and classe not in nouveaux_etats_finaux:
                nouveaux_etats_finaux.append(classe)
        
        # Nouvelles transitions
        nouvelles_transitions = {}
        transitions_vues = set()
        
        for (etat, symbole), destination in self.delta.items():
            if etat in etat_vers_classe and destination in etat_vers_classe:
                classe_source = etat_vers_classe[etat]
                classe_dest = etat_vers_classe[destination]
                
                # Éviter les doublons
                transition_key = (classe_source, symbole)
                if transition_key not in transitions_vues:
                    cle = f"{classe_source},{symbole}"
                    nouvelles_transitions[cle] = [classe_dest]
                    transitions_vues.add(transition_key)
        
        return {
            'alphabet': list(self.alphabet),
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
        try:
            # Sauvegarder l'état original
            etats_originaux = len(self.etats)
            
            # Étape 1: Supprimer les états inaccessibles
            accessibles, inaccessibles = self.supprimer_etats_inaccessibles()
            
            # Si pas d'états accessibles, retourner un automate vide
            if not accessibles:
                return {
                    'alphabet': list(self.alphabet),
                    'etats': [],
                    'etats_initiaux': [],
                    'etats_finaux': [],
                    'transitions': {}
                }, {
                    'etats_inaccessibles': list(inaccessibles),
                    'etats_accessibles': [],
                    'classes_equivalence': {},
                    'nombre_etats_original': etats_originaux,
                    'nombre_etats_minimise': 0,
                    'erreur': 'Aucun état accessible'
                }
            
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
                'nombre_etats_original': etats_originaux,
                'nombre_etats_minimise': len(automate_minimise['etats']),
                'table_distinguabilite': {f"{k[0]}-{k[1]}": v for k, v in table_distinguabilite.items()}
            }
            
            return automate_minimise, info_debug
            
        except Exception as e:
            # En cas d'erreur, retourner l'automate original avec info d'erreur
            return {
                'alphabet': list(self.alphabet),
                'etats': list(self.etats),
                'etats_initiaux': list(self.etats_initiaux),
                'etats_finaux': list(self.etats_finaux),
                'transitions': self.transitions
            }, {
                'erreur': f"Erreur durant la minimisation: {str(e)}",
                'nombre_etats_original': len(self.etats),
                'nombre_etats_minimise': len(self.etats)
            }


def minimiser_automate(automate):
    """
    Fonction utilitaire pour minimiser un automate
    
    Args:
        automate: Dictionnaire représentant l'automate
        
    Returns:
        tuple: (automate_minimise, informations_debug)
    """
    try:
        minimiseur = MinimisationAutomate(automate)
        return minimiseur.minimiser()
    except Exception as e:
        # Retourner l'automate original en cas d'erreur
        return automate, {'erreur': f"Erreur lors de la minimisation: {str(e)}"}


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
    
    print("=== Test de minimisation ===")
    print(f"Automate original:")
    print(f"  États: {automate_test['etats']}")
    print(f"  États initiaux: {automate_test['etats_initiaux']}")
    print(f"  États finaux: {automate_test['etats_finaux']}")
    print(f"  Transitions: {len(automate_test['transitions'])}")
    
    try:
        automate_min, info = minimiser_automate(automate_test)
        
        print(f"\nAutomate minimisé:")
        print(f"  États: {automate_min['etats']}")
        print(f"  États initiaux: {automate_min['etats_initiaux']}")
        print(f"  États finaux: {automate_min['etats_finaux']}")
        print(f"  Transitions: {len(automate_min['transitions'])}")
        
        if 'classes_equivalence' in info:
            print(f"\nClasses d'équivalence:")
            for rep, membres in info['classes_equivalence'].items():
                print(f"  {rep}: {membres}")
        
        print(f"\nRéduction: {info['nombre_etats_original']} → {info['nombre_etats_minimise']} états")
        
        if 'erreur' in info:
            print(f"Erreur: {info['erreur']}")
            
    except Exception as e:
        print(f"Erreur durant le test: {e}")


if __name__ == "__main__":
    test_minimisation()
