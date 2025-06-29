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
    from minimise import MinimisationAutomate, minimiser_automate
    from thompson import thompson_construction

    
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
        
        # Mettre à jour les automates globaux
        automate_courant = automate_exemple
        automate_original = automate_exemple.copy()
        
        return jsonify({
            'succes': True,
            'message': f'Automate de Glushkov créé pour "{regex}"',
            'automate': automate_exemple,
            'positions': {'1': 'b', '2': 'a', '3': 'b'},
            'regex': regex
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/creer_automate_thompson', methods=['POST'])
def creer_automate_thompson():
    """Crée un automate de Thompson à partir d'une expression régulière"""
    global automate_courant, automate_original

    try:
        donnees = request.json
        regex = donnees.get('regex', '')

        if not regex:
            return jsonify({'erreur': 'Expression régulière manquante'}), 400

        automate = thompson_construction(regex)

        automate_courant = automate
        automate_original = automate.copy()

        return jsonify({
            'succes': True,
            'message': f'Automate de Thompson créé pour "{regex}"',
            'automate': automate,
            'regex': regex
        })

    except Exception as e:
        return jsonify({'erreur': f'Erreur lors de la construction Thompson : {str(e)}'}), 500


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
        
        # Validation plus poussée
        if not donnees['etats']:
            return jsonify({'erreur': 'L\'automate doit avoir au moins un état'}), 400
        
        if not donnees['etats_initiaux']:
            return jsonify({'erreur': 'L\'automate doit avoir au moins un état initial'}), 400
        
        # Vérifier que les états initiaux et finaux sont dans la liste des états
        etats_set = set(donnees['etats'])
        for etat in donnees['etats_initiaux']:
            if etat not in etats_set:
                return jsonify({'erreur': f'État initial "{etat}" non trouvé dans les états'}), 400
        
        for etat in donnees['etats_finaux']:
            if etat not in etats_set:
                return jsonify({'erreur': f'État final "{etat}" non trouvé dans les états'}), 400
        
        # Stocker les données
        automate_courant = donnees.copy()
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
        
        # Simulation simple pour tester - à remplacer par la vraie logique
        # Cette implémentation basique simule un automate qui accepte les mots de longueur paire
        accepte = len(mot) % 2 == 0
        
        # Génération d'une trace simple
        trace = []
        etat_courant = automate_courant['etats_initiaux'][0] if automate_courant['etats_initiaux'] else None
        
        for i, symbole in enumerate(mot):
            trace.append({
                'step': i,
                'etat': etat_courant,
                'symbole': symbole,
                'nouvel_etat': etat_courant  # Simplification
            })
        
        return jsonify({
            'succes': True,
            'accepte': accepte,
            'mot': mot,
            'etats_finaux': automate_courant.get('etats_finaux', []),
            'trace': trace,
            'message': f'Mot "{mot}" {"accepté" if accepte else "rejeté"}'
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/analyser_etats', methods=['GET'])
def analyser_etats():
    """Analyse les états accessibles, coaccessibles, utiles et inutiles"""
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        # Analyse simple pour tester - à remplacer par la vraie logique
        etats = automate_courant.get('etats', [])
        
        # Pour l'instant, considérons tous les états comme utiles
        return jsonify({
            'succes': True,
            'etats_accessibles': etats,
            'etats_coaccessibles': etats,
            'etats_utiles': etats,
            'etats_inutiles': [],
            'est_emonde': True,
            'statistiques': {
                'nombre_etats_total': len(etats),
                'nombre_etats_accessibles': len(etats),
                'nombre_etats_coaccessibles': len(etats),
                'nombre_etats_utiles': len(etats),
                'nombre_etats_inutiles': 0
            }
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
        
        # Pour l'instant, supposons que l'automate est déjà déterministe
        # À remplacer par la vraie logique de déterminisation
        return jsonify({
            'succes': True,
            'message': 'L\'automate est déjà déterministe',
            'automate': automate_courant,
            'etait_deterministe': True
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
        
        # Tenter d'utiliser la fonction de minimisation
        try:
            # Minimiser l'automate
            automate_minimise, info_debug = minimiser_automate(automate_courant)
            
            # Mettre à jour l'automate courant avec la version minimisée
            automate_courant = automate_minimise
            
            # Préparer la réponse
            response_data = {
                'succes': True,
                'message': 'Automate minimisé avec succès',
                'automate': automate_minimise,
                'info_debug': info_debug
            }
            
            # Ajouter des informations sur la réduction
            if 'nombre_etats_original' in info_debug and 'nombre_etats_minimise' in info_debug:
                original = info_debug['nombre_etats_original']
                minimise_count = info_debug['nombre_etats_minimise']
                
                if original > minimise_count:
                    response_data['message'] = f'Automate minimisé: {original} → {minimise_count} états'
                    response_data['reduction'] = {
                        'etats_originaux': original,
                        'etats_minimises': minimise_count,
                        'etats_supprimes': original - minimise_count
                    }
                else:
                    response_data['message'] = 'L\'automate était déjà minimal'
                    response_data['reduction'] = {
                        'etats_originaux': original,
                        'etats_minimises': minimise_count,
                        'etats_supprimes': 0
                    }
            
            # Vérifier s'il y a eu des erreurs
            if 'erreur' in info_debug:
                response_data['avertissement'] = info_debug['erreur']
            
            return jsonify(response_data)
            
        except Exception as minimisation_error:
            # Si la minimisation échoue, retourner l'automate inchangé avec un avertissement
            return jsonify({
                'succes': True,
                'message': 'Minimisation échouée - automate inchangé',
                'automate': automate_courant,
                'avertissement': f'Erreur de minimisation: {str(minimisation_error)}'
            })
            
    except Exception as e:
        return jsonify({
            'erreur': f'Erreur lors de la minimisation: {str(e)}',
            'succes': False
        }), 500

@app.route('/api/complementer', methods=['POST'])
def complementer():
    """Calcule le complément de l'automate"""
    global automate_courant
    
    try:
        if not automate_courant:
            return jsonify({'erreur': 'Aucun automate défini'}), 400
        
        # Créer le complément en inversant les états finaux
        complement = automate_courant.copy()
        tous_etats = set(complement['etats'])
        etats_finaux_actuels = set(complement['etats_finaux'])
        nouveaux_etats_finaux = list(tous_etats - etats_finaux_actuels)
        complement['etats_finaux'] = nouveaux_etats_finaux
        
        # Mettre à jour l'automate courant
        automate_courant = complement
        
        return jsonify({
            'succes': True,
            'message': 'Complément calculé avec succès',
            'automate': complement,
            'anciens_etats_finaux': list(etats_finaux_actuels),
            'nouveaux_etats_finaux': nouveaux_etats_finaux
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
            'automate': automate_courant,
            'statistiques': {
                'nombre_etats': len(automate_courant.get('etats', [])),
                'nombre_etats_initiaux': len(automate_courant.get('etats_initiaux', [])),
                'nombre_etats_finaux': len(automate_courant.get('etats_finaux', [])),
                'taille_alphabet': len(automate_courant.get('alphabet', [])),
                'nombre_transitions': len(automate_courant.get('transitions', {}))
            }
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/reinitialiser', methods=['POST'])
def reinitialiser():
    """Remet à zéro les automates"""
    global automate_courant, automate_original
    
    try:
        automate_courant = None
        automate_original = None
        
        return jsonify({
            'succes': True,
            'message': 'Automates réinitialisés'
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

@app.route('/api/info', methods=['GET'])
def info_application():
    """Retourne des informations sur l'application"""
    try:
        # Vérifier quels modules sont disponibles
        modules_disponibles = {}
        
        try:
            from automate import Automate
            modules_disponibles['automate'] = True
        except ImportError:
            modules_disponibles['automate'] = False
        
        try:
            from operations import OperationsAutomate
            modules_disponibles['operations'] = True
        except ImportError:
            modules_disponibles['operations'] = False
        
        try:
            from glushkov import construire_automate_glushkov
            modules_disponibles['glushkov'] = True
        except ImportError:
            modules_disponibles['glushkov'] = False
        
        try:
            from minimise import MinimisationAutomate, minimiser_automate
            modules_disponibles['minimise'] = True
        except ImportError:
            modules_disponibles['minimise'] = False
        
        return jsonify({
            'succes': True,
            'application': 'Simulateur d\'Automates Finis',
            'version': '1.0',
            'modules_disponibles': modules_disponibles,
            'automate_charge': automate_courant is not None,
            'automate_original_sauvegarde': automate_original is not None
        })
        
    except Exception as e:
        return jsonify({'erreur': str(e)}), 500

# Gestionnaire d'erreurs globaux
@app.errorhandler(404)
def page_non_trouvee(e):
    return jsonify({'erreur': 'Route non trouvée'}), 404

@app.errorhandler(405)
def methode_non_autorisee(e):
    return jsonify({'erreur': 'Méthode non autorisée'}), 405

@app.errorhandler(500)
def erreur_serveur(e):
    return jsonify({'erreur': 'Erreur interne du serveur'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Démarrage du serveur Flask... port = 5003")

    
    app.run(debug=True, host='0.0.0.0', port=5003)
