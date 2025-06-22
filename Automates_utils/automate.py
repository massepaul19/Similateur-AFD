# automate.py - Classe principale pour représenter un automate
class Automate:
    """Classe représentant un automate fini"""
    
    def __init__(self, alphabet, etats, etats_initiaux, etats_finaux, transitions):
        self.alphabet = alphabet
        self.etats = etats
        self.etats_initiaux = etats_initiaux if isinstance(etats_initiaux, list) else [etats_initiaux]
        self.etats_finaux = etats_finaux if isinstance(etats_finaux, list) else [etats_finaux]
        self.transitions = transitions
        
    def copier(self):
        """Crée une copie profonde de l'automate"""
        import copy
        return Automate(
            alphabet=copy.deepcopy(self.alphabet),
            etats=copy.deepcopy(self.etats),
            etats_initiaux=copy.deepcopy(self.etats_initiaux),
            etats_finaux=copy.deepcopy(self.etats_finaux),
            transitions=copy.deepcopy(self.transitions)
        )
    
    def vers_dict(self):
        """Convertit l'automate en dictionnaire pour JSON"""
        return {
            'alphabet': self.alphabet,
            'etats': self.etats,
            'etats_initiaux': self.etats_initiaux,
            'etats_finaux': self.etats_finaux,
            'transitions': self.transitions
        }
    
    def simuler_mot(self, mot):
        """Simule l'exécution d'un mot sur l'automate"""
        # Vérifier que tous les symboles du mot sont dans l'alphabet
        for symbole in mot:
            if symbole not in self.alphabet:
                raise ValueError(f"Le symbole '{symbole}' n'est pas dans l'alphabet")
        
        # Commencer avec tous les états initiaux
        etats_courants = set(self.etats_initiaux)
        trace = [{'etats': list(etats_courants), 'symbole': '', 'etape': 0}]
        
        for i, symbole in enumerate(mot):
            etats_suivants = set()
            
            for etat in etats_courants:
                if etat in self.transitions and symbole in self.transitions[etat]:
                    destinations = self.transitions[etat][symbole]
                    if isinstance(destinations, list):
                        etats_suivants.update(destinations)
                    else:
                        etats_suivants.add(destinations)
            
            etats_courants = etats_suivants
            trace.append({
                'etats': list(etats_courants),
                'symbole': symbole,
                'etape': i + 1
            })
            
            # Si plus d'états, arrêter
            if not etats_courants:
                break
        
        # Vérifier si au moins un état final est atteint
        accepte = any(etat in self.etats_finaux for etat in etats_courants)
        
        return {
            'accepte': accepte,
            'etats_finaux': list(etats_courants),
            'trace': trace
        }
    
    def obtenir_transitions_depuis_etat(self, etat):
        """Retourne toutes les transitions depuis un état donné"""
        if etat not in self.transitions:
            return {}
        return self.transitions[etat]
    
    def ajouter_transition(self, etat_source, symbole, etat_destination):
        """Ajoute une transition à l'automate"""
        if etat_source not in self.transitions:
            self.transitions[etat_source] = {}
        
        if symbole not in self.transitions[etat_source]:
            self.transitions[etat_source][symbole] = []
        
        if isinstance(self.transitions[etat_source][symbole], list):
            if etat_destination not in self.transitions[etat_source][symbole]:
                self.transitions[etat_source][symbole].append(etat_destination)
        else:
            # Convertir en liste si ce n'était pas déjà le cas
            ancienne_destination = self.transitions[etat_source][symbole]
            self.transitions[etat_source][symbole] = [ancienne_destination, etat_destination]
