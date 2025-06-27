# routes/automate_routes.py - Routes pour l'API des automates
import traceback
from flask import Blueprint, request, jsonify , render_template
from app.models.automate import db, Automate, AutomateService
from sqlalchemy import func

automate_bp = Blueprint('automate', __name__, url_prefix='/api')

@automate_bp.route('/automates', methods=['POST'])
def create_automate():
    """Créer un nouvel automate"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400

        # 🔍 Étape 1 : validation
        errors = AutomateService.validate_automate_data(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Données invalides',
                'details': errors
            }), 400

        # 🔨 Étape 2 : création
        automate = AutomateService.create_automate(data)

        return jsonify({
            'success': True,
            'message': 'Automate créé avec succès',
            'id': automate.id,
            'automate': automate.to_dict()
        }), 201

    except Exception as e:
        # ⛔ Trace dans la console Flask (pour toi développeur)
        traceback.print_exc()

        # 🔴 Réponse utile pour le front
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': str(e)
        }), 500

@automate_bp.route('/automates/<int:automate_id>', methods=['GET'])
def get_automate(automate_id):
    """Récupérer un automate par son ID"""
    try:
        automate = AutomateService.get_automate(automate_id)
        return jsonify({
            'success': True,
            'automate': automate.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@automate_bp.route('/automates/<int:automate_id>', methods=['PUT'])
def update_automate(automate_id):
    """Mettre à jour un automate"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Validation des données
        errors = AutomateService.validate_automate_data(data)
        if errors:
            return jsonify({'error': 'Données invalides', 'details': errors}), 400
        
        # Mettre à jour l'automate
        automate = AutomateService.update_automate(automate_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Automate mis à jour avec succès',
            'automate': automate.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automate_bp.route('/automates/<int:automate_id>', methods=['DELETE'])
def delete_automate(automate_id):
    """Supprimer un automate"""
    try:
        AutomateService.delete_automate(automate_id)
        return jsonify({
            'success': True,
            'message': 'Automate supprimé avec succès'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automate_bp.route('/automates', methods=['GET'])
def list_automates():
    """Lister tous les automates"""
    try:
        automates = AutomateService.list_automates()
        return jsonify({
            'success': True,
            'automates': [automate.to_dict() for automate in automates]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automate_bp.route('/automates/<int:automate_id>/validate', methods=['POST'])
def validate_automate(automate_id):
    """Valider un automate selon son type"""
    try:
        automate = AutomateService.get_automate(automate_id)
        
        # Logique de validation selon le type
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Vérifications communes
        if not automate.initial_state:
            validation_result['errors'].append("Aucun état initial défini")
            validation_result['is_valid'] = False
        
        final_states = [s for s in automate.states if s.is_final]
        if not final_states:
            validation_result['errors'].append("Aucun état final défini")
            validation_result['is_valid'] = False
        
        # Vérifications spécifiques selon le type
        if automate.type == 'afdc':
            # Vérifier la complétude
            states = {s.state_id for s in automate.states}
            alphabet = set(automate.alphabet)
            alphabet.discard('ε')
            
            existing_transitions = {}
            for t in automate.transitions:
                key = f"{t.from_state},{t.symbol}"
                if key not in existing_transitions:
                    existing_transitions[key] = []
                existing_transitions[key].append(t.to_state)
            
            for state in states:
                for symbol in alphabet:
                    key = f"{state},{symbol}"
                    if key not in existing_transitions:
                        validation_result['errors'].append(f"Transition manquante: {state} --{symbol}-->")
                        validation_result['is_valid'] = False
        
        elif automate.type == 'afd':
            # Vérifier le déterminisme
            transition_keys = {}
            for t in automate.transitions:
                key = f"{t.from_state},{t.symbol}"
                if key in transition_keys:
                    validation_result['errors'].append(f"Transition non-déterministe: {key}")
                    validation_result['is_valid'] = False
                transition_keys[key] = True
        
        return jsonify({
            'success': True,
            'validation': validation_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@automate_bp.route('/mes-automates')
def my_automata():
    """Afficher la page des automates avec les données de la BD"""
    try:
        # Récupérer tous les automates
        automates = AutomateService.list_automates()
        
        # Calculer les statistiques
        stats = {
            'total': len(automates),
            'types': len(set(automate.type for automate in automates)),
            'operations': sum(len(automate.states) + len(automate.transitions) for automate in automates)
        }
        
        # Compter par type
        type_counts = {}
        for automate in automates:
            type_counts[automate.type] = type_counts.get(automate.type, 0) + 1
        
        # Préparer les données pour le template
        automates_data = []
        for automate in automates:
            automate_dict = automate.to_dict()
            # Ajouter des informations calculées
            automate_dict['states_count'] = len(automate.states)
            automate_dict['transitions_count'] = len(automate.transitions)
            automate_dict['alphabet_str'] = ','.join(automate.alphabet)
            automates_data.append(automate_dict)
        
        return render_template('mes_automates.html', 
                             automates=automates_data,
                             stats=stats,
                             type_counts=type_counts)
    
    except Exception as e:
        # En cas d'erreur, passer des valeurs par défaut
        return render_template('mes_automates.html', 
                             automates=[],
                             stats={'total': 0, 'types': 0, 'operations': 0},
                             type_counts={},
                             error=str(e))
@automate_bp.route('/api/automates')
def api_automates():
    """API pour récupérer les automates en JSON"""
    try:
        automates = AutomateService.list_automates()
        return jsonify({
            'success': True,
            'automates': [automate.to_dict() for automate in automates]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automate_bp.route('/api/automates/<int:automate_id>')
def api_automate_detail(automate_id):
    """API pour récupérer un automate spécifique"""
    try:
        automate = AutomateService.get_automate(automate_id)
        return jsonify({
            'success': True,
            'automate': automate.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@automate_bp.route('/api/automates/<int:automate_id>', methods=['DELETE'])
def api_delete_automate(automate_id):
    """API pour supprimer un automate"""
    try:
        AutomateService.delete_automate(automate_id)
        return jsonify({
            'success': True,
            'message': 'Automate supprimé avec succès'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
from flask import jsonify

@automate_bp.route('/api/automates/<int:automate_id>/graph-data')
def get_automate_graph_data(automate_id):
    """
    Retourne les données nécessaires pour générer le graphe d'un automate
    """
    try:
        # Récupérer l'automate depuis votre base de données
        # Adaptez cette partie selon votre modèle de données
        automate = Automate.query.get_or_404(automate_id)
        
        # Formatter les données pour le frontend
        graph_data = {
            'id': automate.id,
            'states': [
                {
                    'state_id': state.state_id,
                    'is_initial': state.is_initial,
                    'is_final': state.is_final
                }
                for state in automate.states
            ],
            'transitions': [
                {
                    'from_state': transition.from_state,
                    'to_state': transition.to_state,
                    'symbol': transition.symbol if transition.symbol else 'ε'
                }
                for transition in automate.transitions
            ],
            'alphabet': list(automate.alphabet) if hasattr(automate, 'alphabet') else []
        }
        
        return jsonify(graph_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la récupération des données: {str(e)}'
        }), 500

# Route alternative si vous avez une structure de données différente
