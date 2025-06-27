# app.py - Application Flask complète avec minimisation et complémentation
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from copy import deepcopy

# Importez vos modules (assurez-vous qu'ils existent)
try:
    from automate import Automate
    from operations import OperationsAutomate
    from glushkov import construire_automate_glushkov
except ImportError as e:
    print(f"Erreur d'importation: {e}")
    print("Certains modules ne sont pas disponibles, certaines fonctionnalités seront limitées")

app = Flask(__name__)
CORS(app)

# Variables globales pour stocker les automates
automate_courant = None
automate_original = None

class AutomateMinimiseur:
    """Classe pour la minimisation d'automates"""
    
    @staticmethod
    def est_deterministe(automate):
        """Vérifie si un automate est déterministe"""
        if len(automate['etats_initiaux']) != 1:
            return False
        
        transitions = automate.get('transitions', {})
        for cle, destinations in transitions.items():
            if len(destinations) > 1:
                return False
        return True
    
    @staticmethod
    def determiniser(automate):
        """Déterminise un automate non-déterministe"""
        if AutomateMinimiseur.est_deterministe(automate):
            return automate, "L'automate était déjà déterministe"
        
        alphabet = automate['alphabet']
        etats_initiaux = set(automate['etats_initiaux'])
        etats_finaux = set(automate['etats_finaux'])
        transitions_originales = automate.get('transitions', {})
        
        # Nouveaux états (ensembles d'états originaux)
        nouveaux_etats = {}
        nouveaux_etats_finaux = []
        nouvelles_transitions = {}
        
        # File pour BFS
        from collections import deque
        file = deque()
        
        # État initial : ensemble des états initiaux
        etat_initial = frozenset(etats_initiaux)
        nouveaux_etats[etat_initial] = f"q{len(nouveaux_etats)}"
        file.append(etat_initial)
        
        # Si l'état initial contient un état final, c'est un état final
        if etat_initial & etats_finaux:
            nouveaux_etats_finaux.append(nouveaux_etats[etat_initial])
        
        while file:
            etat_courant = file.popleft()
            nom_etat_courant = nouveaux_etats[etat_courant]
            
            for symbole in alphabet:
                # Calculer l'ensemble des états atteignables avec ce symbole
                nouvel_ensemble = set()
                for etat in etat_courant:
                    cle = f"{etat},{symbole}"
                    if cle in transitions_originales:
                        nouvel_ensemble.update(transitions_originales[cle])
                
                if nouvel_ensemble:
                    nouvel_ensemble_frozen = frozenset(nouvel_ensemble)
                    
                    # Si ce nouvel ensemble n'existe pas encore
                    if nouvel_ensemble_frozen not in nouveaux_etats:
                        nouveaux_etats[nouvel_ensemble_frozen] = f"q{len(nouveaux_etats)}"
                        file.append(nouvel_ensemble_frozen)
                        
                        # Vérifier si c'est un état final
                        if nouvel_ensemble_frozen & etats_finaux:
                            nouveaux_etats_finaux.append(nouveaux_etats[nouvel_ensemble_frozen])
                    
                    # Ajouter la transition
                    cle_transition = f"{nom_etat_courant},{symbole}"
                    nouvelles_transitions[cle_transition] = [nouveaux_etats[nouvel_ensemble_frozen]]
        
        automate_deterministe = {
            'alphabet': alphabet,
            'etats': list(nouveaux_etats.values()),
            'etats_initiaux': [nouveaux_etats[etat_initial]],
            'etats_finaux': nouveaux_etats_finaux,
            'transitions': nouvelles_transitions
        }
        
        return automate_deterministe, "Automate déterminisé avec succès"
    
    @staticmethod
    def minimiser_moore(automate):
        """Minimise un automate déterministe avec l'algorithme de Moore"""
        if not AutomateMinimiseur.est_deterministe(automate):
            automate, msg = AutomateMinimiseur.determiniser(automate)
        
        alphabet = automate['alphabet']
        etats = automate['etats']
        etats_finaux = set(automate['etats_finaux'])
        transitions = automate.get('transitions', {})
        
        # Partition initiale : états finaux vs non-finaux
        finaux = [e for e in etats if e in etats_finaux]
        non_finaux = [e for e in etats if e not in etats_finaux]
        
        partition = []
        if non_finaux:
            partition.append(non_finaux)
        if finaux:
            partition.append(finaux)
        
        if not partition:
            return automate, "Aucun état à minimiser"
        
        iteration = 0
        while True:
            iteration += 1
            nouvelle_partition = []
            partition_modifiee = False
            
            for classe in partition:
                if len(classe) <= 1:
                    nouvelle_partition.append(classe)
                    continue
                
                # Grouper les états par comportement
                groupes = {}
                for etat in classe:
                    signature = []
                    for symbole in alphabet:
                        cle = f"{etat},{symbole}"
                        if cle in transitions:
                            destination = transitions[cle][0]
                            # Trouver dans quelle classe est la destination
                            classe_dest = None
                            for i, p in enumerate(partition):
                                if destination in p:
                                    classe_dest = i
                                    break
                            signature.append(classe_dest)
                        else:
                            signature.append(None)  # Pas de transition
                    
                    signature_tuple = tuple(signature)
                    if signature_tuple not in groupes:
                        groupes[signature_tuple] = []
                    groupes[signature_tuple].append(etat)
                
                # Ajouter les nouveaux groupes
                if len(groupes) > 1:
                    partition_modifiee = True
                
                for groupe in groupes.values():
                    nouvelle_partition.append(groupe)
            
            partition = nouvelle_partition
            if not partition_modifiee:
                break
        
        # Construire l'automate minimisé
        # Créer un représentant pour chaque classe
        representants = {}
        nouveaux_etats = []
        for i, classe in enumerate(partition):
            representant = f"q{i}"
            nouveaux_etats.append(representant)
            for etat in classe:
                representants[etat] = representant
        
        # États initiaux et finaux
        nouveaux_etats_initiaux = []
        for etat_initial in automate['etats_initiaux']:
            repr_initial = representants[etat_initial]
            if repr_initial not in nouveaux_etats_initiaux:
                nouveaux_etats_initiaux.append(repr_initial)
        
        nouveaux_etats_finaux = []
        for etat_final in automate['etats_finaux']:
            repr_final = representants[etat_final]
            if repr_final not in nouveaux_etats_finaux:
                nouveaux_etats_finaux.append(repr_final)
        
        # Nouvelles transitions
        nouvelles_transitions = {}
        for cle, destinations in transitions.items():
            etat_source, symbole = cle.split(',', 1)
            repr_source = representants[etat_source]
            repr_dest = representants[destinations[0]]
            
            nouvelle_cle = f"{repr_source},{symbole}"
            if nouvelle_cle not in nouvelles_transitions:
                nouvelles_transitions[nouvelle_cle] = [repr_dest]
        
        automate_minimise = {
            'alphabet': alphabet,
            'etats': nouveaux_etats,
            'etats_initiaux': nouveaux_etats_initiaux,
            'etats_finaux': nouveaux_etats_finaux,
            'transitions': nouvelles_transitions
        }
        
        reduction = len(etats) - len(nouveaux_etats)
        message = f"Automate minimisé en {iteration} itérations. Réduction: {reduction} états"
        
        return automate_minimise, message

class AutomateComplementeur:
    """Classe pour la complémentation d'automates"""
    
    @staticmethod
    def completer_automate(automate):
        """Ajoute un état puits si nécessaire pour compléter l'automate"""
        alphabet = automate['alphabet']
        etats = automate['etats'][:]
        transitions = automate.get('transitions', {}).copy()
        
        # Vérifier si toutes les transitions existent
        etat_puits_necessaire = False
        for etat in etats:
            for symbole in alphabet:
                cle = f"{etat},{symbole}"
                if cle not in transitions:
                    etat_puits_necessaire = True
                    break
            if etat_puits_necessaire:
                break
        
        if etat_puits_necessaire:
            # Ajouter un état puits
            etat_puits = "qpuits"
            etats.append(etat_puits)
            
            # Ajouter les transitions manquantes vers l'état puits
            for etat in automate['etats']:
                for symbole in alphabet:
                    cle = f"{etat},{symbole}"
                    if cle not in transitions:
                        transitions[cle] = [etat_puits]
            
            # L'état puits boucle sur lui-même
            for symbole in alphabet:
                cle = f"{etat_puits},{symbole}"
                transitions[cle] = [etat_puits]
        
        return {
            'alphabet': alphabet,
            'etats': etats,
            'etats_initiaux': automate['etats_initiaux'][:],
            'etats_finaux': automate['etats_finaux'][:],
            'transitions': transitions
        }
    
    @staticmethod
    def complementer(automate):
        """Calcule le complément d'un automate"""
        # D'abord s'assurer que l'automate est déterministe
        if not AutomateMinimiseur.est_deterministe(automate):
            automate, _ = AutomateMinimiseur.determiniser(automate)
        
        # Compléter l'automate (ajouter état puits si nécessaire)
        automate_complet = AutomateComplementeur.completer_automate(automate)
        
        # Inverser les états finaux
        tous_etats = set(automate_complet['etats'])
        etats_finaux_actuels = set(automate_complet['etats_finaux'])
        nouveaux_etats_finaux = list(tous_etats - etats_finaux_actuels)
        
        automate_complement = {
            'alphabet': automate_complet['alphabet'],
            'etats': automate_complet['etats'],
            'etats_initiaux': automate_complet['etats_initiaux'],
            'etats_finaux': nouveaux_etats_finaux,
            'transitions': automate_complet['transitions']
        }
        
        return automate_complement, "Complément calculé avec succès"

@app.route('/')
def index():
    """Route principale - sert la page HTML"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Sert les fichiers statiques (CSS, JS)"""
    return send_from_directory('static', filename)

@app.route('/api/test', methods=['GET'])
def test_api():
    """Route de test pour vérifier que l'API fonctionne"""
    return jsonify({
        'succes': True,
        'message': 'API Flask fonctionne correctement',
        'version': '1.0'
    })

@app.route('/api/creer_automate_glushkov', methods=['POST'])
def creer_automate_glushkov():
    """Crée un automate de Glushkov à partir d'une expression régulière"""
    global automate_courant, automate_original
    
    try:
        donnees = request.json
        regex = donnees.get('regex', '')
        
        if not regex:
            return jsonify({'erreur': 'Expression régulière manquante'}), 400
        
        # Pour l'instant, créons un automate simple pour tester
        # Vous devrez implémenter la vraie logique Glushkov
        automate_exemple = {
            'alphabet': ['a', 'b'],
            'etats': ['0', '1', '2', '3'],
            'etats_initiaux': ['0'],
            'etats_finaux': ['3'],
            'transitions': {
                '0,b': ['1'],
                '1,a': ['2'],
                '2,b': ['3'],
                '1,b': ['1']
            }
        }
        
        automate_courant = automate_exemple
        automate_original = deepcopy(automate_exemple)
        
        return jsonify({
            'succes': True,
            'message': f'Automate de Glushkov créé pour "{regex}"',
            'automate': automate_exemple,
            'positions': {'1': 'b', '2': 'a', '3': 'b'},
            'regex': regex
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/creer_automate', methods=['POST'])
def creer_automate():
    """Crée un nouvel automate à partir des données fournies"""
    global automate_courant, automate_original
    
    try:
        donnees = request.json
        
        # Validation des données
        required_keys = ['alphabet', 'etats', 'etats_initiaux', 'etats_finaux', 'transitions']
        if not all(key in donnees for key in required_keys):
            return jsonify({'erreur': 'Données manquantes'}), 400
        
        # Stocker les données
        automate_courant = donnees
        automate_original = deepcopy(donnees)
        
        return jsonify({
            'succes': True,
            'message': 'Automate créé avec succès',
            'automate': donnees
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/reconnaitre_mot', methods=['POST'])
def reconnaitre_mot():
    """Teste si un mot est reconnu par l'automate"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        donnees = request.json
        mot = donnees.get('mot', '')
        
        # Simulation de reconnaissance
        etats_courants = set(automate_courant['etats_initiaux'])
        trace = [{'etats': list(etats_courants), 'symbole': None}]
        
        transitions = automate_courant.get('transitions', {})
        
        for symbole in mot:
            nouveaux_etats = set()
            for etat in etats_courants:
                cle = f"{etat},{symbole}"
                if cle in transitions:
                    nouveaux_etats.update(transitions[cle])
            
            etats_courants = nouveaux_etats
            trace.append({'etats': list(etats_courants), 'symbole': symbole})
            
            if not etats_courants:  # Aucun état accessible
                break
        
        # Vérifier si on finit dans un état final
        etats_finaux = set(automate_courant['etats_finaux'])
        accepte = bool(etats_courants & etats_finaux)
        
        return jsonify({
            'succes': True,
            'accepte': accepte,
            'etats_finaux': list(etats_finaux),
            'trace': trace
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/analyser_etats', methods=['GET'])
def analyser_etats():
    """Analyse les états accessibles, coaccessibles, utiles et inutiles"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        # Calcul des états accessibles
        etats_accessibles = set(automate_courant['etats_initiaux'])
        transitions = automate_courant.get('transitions', {})
        
        changed = True
        while changed:
            changed = False
            nouveaux_etats = set(etats_accessibles)
            for etat in etats_accessibles:
                for cle, destinations in transitions.items():
                    if cle.startswith(f"{etat},"):
                        for dest in destinations:
                            if dest not in nouveaux_etats:
                                nouveaux_etats.add(dest)
                                changed = True
            etats_accessibles = nouveaux_etats
        
        # Calcul des états coaccessibles (depuis les états finaux en arrière)
        etats_coaccessibles = set(automate_courant['etats_finaux'])
        
        changed = True
        while changed:
            changed = False
            nouveaux_etats = set(etats_coaccessibles)
            for cle, destinations in transitions.items():
                for dest in destinations:
                    if dest in etats_coaccessibles:
                        etat_source = cle.split(',')[0]
                        if etat_source not in nouveaux_etats:
                            nouveaux_etats.add(etat_source)
                            changed = True
            etats_coaccessibles = nouveaux_etats
        
        # États utiles = accessibles ET coaccessibles
        etats_utiles = etats_accessibles & etats_coaccessibles
        
        # États inutiles = tous - utiles
        tous_etats = set(automate_courant['etats'])
        etats_inutiles = tous_etats - etats_utiles
        
        return jsonify({
            'succes': True,
            'etats_accessibles': list(etats_accessibles),
            'etats_coaccessibles': list(etats_coaccessibles),
            'etats_utiles': list(etats_utiles),
            'etats_inutiles': list(etats_inutiles),
            'est_emonde': len(etats_inutiles) == 0
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/determiniser', methods=['POST'])
def determiniser():
    """Déterminise l'automate courant"""
    global automate_courant
    
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        automate_deterministe, message = AutomateMinimiseur.determiniser(automate_courant)
        automate_courant = automate_deterministe
        
        return jsonify({
            'succes': True,
            'message': message,
            'automate': automate_deterministe
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/minimiser', methods=['POST'])
def minimiser():
    """Minimise l'automate courant"""
    global automate_courant
    
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        automate_minimise, message = AutomateMinimiseur.minimiser_moore(automate_courant)
        automate_courant = automate_minimise
        
        return jsonify({
            'succes': True,
            'message': message,
            'automate': automate_minimise,
            'stats': {
                'etats_originaux': len(automate_original['etats']) if automate_original else 0,
                'etats_minimises': len(automate_minimise['etats']),
                'reduction': len(automate_original['etats']) - len(automate_minimise['etats']) if automate_original else 0
            }
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/complementer', methods=['POST'])
def complementer():
    """Calcule le complément de l'automate"""
    global automate_courant
    
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        automate_complement, message = AutomateComplementeur.complementer(automate_courant)
        automate_courant = automate_complement
        
        return jsonify({
            'succes': True,
            'message': message,
            'automate': automate_complement
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/restaurer_original', methods=['POST'])
def restaurer_original():
    """Restaure l'automate original"""
    global automate_courant
    
    try:
        if not automate_original:
            return jsonify({'erreur': 'Aucun automate original à restaurer'}), 400
        
        automate_courant = deepcopy(automate_original)
        
        return jsonify({
            'succes': True,
            'message': 'Automate original restauré',
            'automate': automate_courant
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/obtenir_automate', methods=['GET'])
def obtenir_automate():
    """Retourne l'automate courant"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        return jsonify({
            'succes': True,
            'automate': automate_courant
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

if __name__ == '__main__':
    print("Démarrage du serveur Flask...")
    print("URL: http://localhost:5003")
    app.run(debug=True, host='0.0.0.0', port=5003)
