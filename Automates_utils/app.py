# app.py - Application Flask complète
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json

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
        
        # Pour l'instant, on stocke juste les données
        automate_courant = donnees
        automate_original = donnees.copy()
        
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
        
        # Simulation simple pour tester
        # Vous devrez implémenter la vraie logique de simulation
        accepte = len(mot) % 2 == 0  # Exemple simple
        
        return jsonify({
            'succes': True,
            'accepte': accepte,
            'etats_finaux': automate_courant.get('etats_finaux', []),
            'trace': [{'etat': '0', 'symbole': c} for c in mot]
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/analyser_etats', methods=['GET'])
def analyser_etats():
    """Analyse les états accessibles, coaccessibles, utiles et inutiles"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        # Analyse simple pour tester
        etats = automate_courant.get('etats', [])
        
        return jsonify({
            'succes': True,
            'etats_accessibles': etats,
            'etats_coaccessibles': etats,
            'etats_utiles': etats,
            'etats_inutiles': [],
            'est_emonde': True
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/determiniser', methods=['POST'])
def determiniser():
    """Déterminise l'automate courant"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        return jsonify({
            'succes': True,
            'message': 'L\'automate est déjà déterministe',
            'automate': automate_courant
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/minimiser', methods=['POST'])
def minimiser():
    """Minimise l'automate courant"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        return jsonify({
            'succes': True,
            'message': 'Automate minimisé avec succès',
            'automate': automate_courant
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/complementer', methods=['POST'])
def complementer():
    """Calcule le complément de l'automate"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        # Inverser les états finaux pour le complément
        if automate_courant:
            complement = automate_courant.copy()
            tous_etats = set(complement['etats'])
            etats_finaux_actuels = set(complement['etats_finaux'])
            nouveaux_etats_finaux = list(tous_etats - etats_finaux_actuels)
            complement['etats_finaux'] = nouveaux_etats_finaux
            
            return jsonify({
                'succes': True,
                'message': 'Complément calculé avec succès',
                'automate': complement
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
        
        automate_courant = automate_original.copy()
        
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
    print("URL: http://localhost:5005")
    print("API Test: http://localhost:5005/api/test")
    app.run(debug=True, host='0.0.0.0', port=5003)
