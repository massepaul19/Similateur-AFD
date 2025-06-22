# operations.py - Classe pour les opérations sur les automates
from automate import Automate

class OperationsAutomate:
    """Classe contenant toutes les opérations sur les automates"""
    
    def __init__(self, automate):
        self.automate = automate
    
    def est_deterministe(self):
        """Vérifie si l'automate est déterministe"""
        # Plus d'un état initial = non déterministe
        if len(self.automate.etats_initiaux) > 1:
            return False
        
        # Vérifier chaque transition
        for etat in self.automate.transitions:
            for symbole in self.automate.transitions[etat]:
                destinations = self.automate.transitions[etat][symbole]
                # Si plus d'une destination = non déterministe
                if isinstance(destinations, list) and len(destinations) > 1:
                    return False
        
        return True
    
    def est_complet(self):
        """Vérifie si l'automate est complet"""
        for etat in self.automate.etats:
            for symbole in self.automate.alphabet:
                if (etat not in self.automate.transitions or 
                    symbole not in self.automate.transitions[etat] or 
                    not self.automate.transitions[etat][symbole]):
                    return False
        return True
    
    def trouver_etats_accessibles(self):
        """Trouve tous les états accessibles depuis les états initiaux"""
        accessibles = set(self.automate.etats_initiaux)
        a_visiter = list(self.automate.etats_initiaux)
        
        while a_visiter:
            etat_courant = a_visiter.pop()
            
            if etat_courant in self.automate.transitions:
                for symbole in self.automate.transitions[etat_courant]:
                    destinations = self.automate.transitions[etat_courant][symbole]
                    if isinstance(destinations, list):
                        for dest in destinations:
                            if dest not in accessibles:
                                accessibles.add(dest)
                                a_visiter.append(dest)
                    else:
                        if destinations not in accessibles:
                            accessibles.add(destinations)
                            a_visiter.append(destinations)
        
        return list(accessibles)
    
    def trouver_etats_coaccessibles(self):
        """Trouve tous les états coaccessibles (qui peuvent atteindre un état final)"""
        coaccessibles = set(self.automate.etats_finaux)
        change = True
        
        while change:
            change = False
            for etat in self.automate.etats:
                if etat not in coaccessibles:
                    if etat in self.automate.transitions:
                        for symbole in self.automate.transitions[etat]:
                            destinations = self.automate.transitions[etat][symbole]
                            if isinstance(destinations, list):
                                if any(dest in coaccessibles for dest in destinations):
                                    coaccessibles.add(etat)
                                    change = True
                                    break
                            else:
                                if destinations in coaccessibles:
                                    coaccessibles.add(etat)
                                    change = True
                                    break
        
        return list(coaccessibles)
    
    def trouver_etats_utiles(self):
        """Trouve les états à la fois accessibles et coaccessibles"""
        accessibles = set(self.trouver_etats_accessibles())
        coaccessibles = set(self.trouver_etats_coaccessibles())
        return list(accessibles.intersection(coaccessibles))
    
    def trouver_etats_inutiles(self):
        """Trouve les états inutiles (ni accessibles ni coaccessibles)"""
        utiles = set(self.trouver_etats_utiles())
        tous_etats = set(self.automate.etats)
        return list(tous_etats.difference(utiles))
    
    def est_emonde(self):
        """Vérifie si l'automate est émondé (sans états inutiles)"""
        return len(self.trouver_etats_inutiles()) == 0
    
    def determiniser(self):
        """Déterminise l'automate en utilisant la construction par sous-ensembles"""
        nouveaux_etats = []
        nouvelles_transitions = {}
        correspondance_etats = {}
        file_attente = []
        
        # État initial = ensemble des états initiaux
        etat_initial_ensemble = tuple(sorted(self.automate.etats_initiaux))
        nouveaux_etats.append(0)
        correspondance_etats[etat_initial_ensemble] = 0
        file_attente.append({'etats': etat_initial_ensemble, 'id': 0})
        
        prochain_id_etat = 1
        
        while file_attente:
            courant = file_attente.pop(0)
            nouvelles_transitions[courant['id']] = {}
            
            for symbole in self.automate.alphabet:
                etats_suivants = set()
                
                for etat in courant['etats']:
                    if (etat in self.automate.transitions and 
                        symbole in self.automate.transitions[etat]):
                        destinations = self.automate.transitions[etat][symbole]
                        if isinstance(destinations, list):
                            etats_suivants.update(destinations)
                        else:
                            etats_suivants.add(destinations)
                
                if etats_suivants:
                    ensemble_suivant = tuple(sorted(etats_suivants))
                    
                    if ensemble_suivant not in correspondance_etats:
                        correspondance_etats[ensemble_suivant] = prochain_id_etat
                        nouveaux_etats.append(prochain_id_etat)
                        file_attente.append({
                            'etats': ensemble_suivant,
                            'id': prochain_id_etat
                        })
                        prochain_id_etat += 1
                    
                    nouvelles_transitions[courant['id']][symbole] = [correspondance_etats[ensemble_suivant]]
        
        # Nouveaux états finaux
        nouveaux_etats_finaux = []
        for i in range(len(nouveaux_etats)):
            ensemble_etat = None
            for ensemble, id_etat in correspondance_etats.items():
                if id_etat == i:
                    ensemble_etat = ensemble
                    break
            
            if ensemble_etat and any(etat in self.automate.etats_finaux for etat in ensemble_etat):
                nouveaux_etats_finaux.append(i)
        
        return Automate(
            alphabet=self.automate.alphabet,
            etats=nouveaux_etats,
            etats_initiaux=[0],  # Un seul état initial après déterminisation
            etats_finaux=nouveaux_etats_finaux,
            transitions=nouvelles_transitions
        )
    
    def minimiser(self):
        """Minimise l'automate en utilisant l'algorithme de Moore"""
        # D'abord s'assurer que l'automate est déterministe
        automate_det = self.automate
        if not self.est_deterministe():
            automate_det = self.determiniser()
        
        ops_det = OperationsAutomate(automate_det)
        
        # Partitionnement initial : états finaux et non-finaux
        etats_finaux = set(automate_det.etats_finaux)
        etats_non_finaux = set(automate_det.etats) - etats_finaux
        
        partitions = []
        if etats_non_finaux:
            partitions.append(list(etats_non_finaux))
        if etats_finaux:
            partitions.append(list(etats_finaux))
        
        # Raffinement des partitions
        change = True
        while change:
            change = False
            nouvelles_partitions = []
            
            for partition in partitions:
                sous_partitions = {}
                
                for etat in partition:
                    signature = []
                    for symbole in automate_det.alphabet:
                        if (etat in automate_det.transitions and 
                            symbole in automate_det.transitions[etat]):
                            destination = automate_det.transitions[etat][symbole]
                            if isinstance(destination, list):
                                destination = destination[0] if destination else None
                            
                            # Trouver la partition de la destination
                            partition_dest = -1
                            for i, p in enumerate(partitions):
                                if destination in p:
                                    partition_dest = i
                                    break
                            signature.append(partition_dest)
                        else:
                            signature.append(-1)  # Pas de transition
                    
                    signature_tuple = tuple(signature)
                    if signature_tuple not in sous_partitions:
                        sous_partitions[signature_tuple] = []
                    sous_partitions[signature_tuple].append(etat)
                
                # Si la partition s'est divisée, marquer le changement
                if len(sous_partitions) > 1:
                    change = True
                
                nouvelles_partitions.extend(sous_partitions.values())
            
            partitions = nouvelles_partitions
        
        # Construire le nouvel automate minimisé
        correspondance_etats = {}
        nouveaux_etats = []
        
        for i, partition in enumerate(partitions):
            nouveaux_etats.append(i)
            for etat in partition:
                correspondance_etats[etat] = i
        
        # Nouvel état initial
        nouvel_etat_initial = correspondance_etats[automate_det.etats_initiaux[0]]
        
        # Nouveaux états finaux
        nouveaux_etats_finaux = []
        for etat_final in automate_det.etats_finaux:
            nouvel_etat = correspondance_etats[etat_final]
            if nouvel_etat not in nouveaux_etats_finaux:
                nouveaux_etats_finaux.append(nouvel_etat)
        
        # Nouvelles transitions
        nouvelles_transitions = {}
        for i in nouveaux_etats:
            nouvelles_transitions[i] = {}
        
        for partition in partitions:
            representant = partition[0]  # Prendre un représentant de la partition
            nouvel_etat_source = correspondance_etats[representant]
            
            if representant in automate_det.transitions:
                for symbole in automate_det.transitions[representant]:
                    destination = automate_det.transitions[representant][symbole]
                    if isinstance(destination, list):
                        destination = destination[0] if destination else None
                    
                    if destination is not None:
                        nouvel_etat_dest = correspondance_etats[destination]
                        nouvelles_transitions[nouvel_etat_source][symbole] = [nouvel_etat_dest]
        
        return Automate(
            alphabet=automate_det.alphabet,
            etats=nouveaux_etats,
            etats_initiaux=[nouvel_etat_initial],
            etats_finaux=nouveaux_etats_finaux,
            transitions=nouvelles_transitions
        )
    
    def completer(self):
        """Complete l'automate en ajoutant un état puits si nécessaire"""
        if self.est_complet():
            return self.automate.copier()
        
        # Créer une copie de l'automate
        nouvel_automate = self.automate.copier()
        
        # Trouver un nouvel ID pour l'état puits
        max_etat = max(nouvel_automate.etats) if nouvel_automate.etats else -1
        etat_puits = max_etat + 1
        
        # Ajouter l'état puits
        nouvel_automate.etats.append(etat_puits)
        nouvel_automate.transitions[etat_puits] = {}
        
        # L'état puits boucle sur lui-même pour tous les symboles
        for symbole in nouvel_automate.alphabet:
            nouvel_automate.transitions[etat_puits][symbole] = [etat_puits]
        
        # Compléter les transitions manquantes
        for etat in nouvel_automate.etats:
            if etat != etat_puits:  # Ne pas traiter l'état puits lui-même
                if etat not in nouvel_automate.transitions:
                    nouvel_automate.transitions[etat] = {}
                
                for symbole in nouvel_automate.alphabet:
                    if symbole not in nouvel_automate.transitions[etat]:
                        nouvel_automate.transitions[etat][symbole] = [etat_puits]
        
        return nouvel_automate
    
    def complementer(self):
        """Calcule le complément de l'automate"""
        # D'abord compléter et déterminiser l'automate
        automate_complet = self.completer()
        
        if not OperationsAutomate(automate_complet).est_deterministe():
            automate_complet = OperationsAutomate(automate_complet).determiniser()
        
        # Inverser les états finaux et non-finaux
        nouveaux_etats_finaux = []
        for etat in automate_complet.etats:
            if etat not in automate_complet.etats_finaux:
                nouveaux_etats_finaux.append(etat)
        
        return Automate(
            alphabet=automate_complet.alphabet,
            etats=automate_complet.etats,
            etats_initiaux=automate_complet.etats_initiaux,
            etats_finaux=nouveaux_etats_finaux,
            transitions=automate_complet.transitions
        )
    
    def compter_transitions(self):
        """Compte le nombre total de transitions"""
        compteur = 0
        for etat in self.automate.transitions:
            for symbole in self.automate.transitions[etat]:
                destinations = self.automate.transitions[etat][symbole]
                if isinstance(destinations, list):
                    compteur += len(destinations)
                else:
                    compteur += 1 if destinations is not None else 0
        return compteur
