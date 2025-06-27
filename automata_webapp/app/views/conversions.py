from flask import Blueprint, render_template, request, jsonify
from app.services.conversion_service import ConversionService

conversions_bp = Blueprint('conversions', __name__)

@conversions_bp.route('/nfa-to-dfa', methods=['GET', 'POST'])
def nfa_to_dfa():
    """Conversion AFN vers AFD"""
    if request.method == 'POST':
        # TODO: Traiter la conversion
        data = request.get_json()
        result = ConversionService.nfa_to_dfa(data)
        return jsonify(result)
    return render_template('conversions/nfa_to_dfa.html')

@conversions_bp.route('/dfa-to-complete', methods=['GET', 'POST'])
def dfa_to_complete():
    """Conversion AFD vers AFDC"""
    if request.method == 'POST':
        data = request.get_json()
        result = ConversionService.dfa_to_complete_dfa(data)
        return jsonify(result)
    return render_template('conversions/dfa_to_complete.html')

@conversions_bp.route('/epsilon-conversions', methods=['GET', 'POST'])
def epsilon_conversions():
    """Gestion des conversions avec epsilon-transitions"""
    if request.method == 'POST':
        conversion_type = request.json.get('type')
        data = request.json.get('data')
        
        if conversion_type == 'epsilon_nfa_to_dfa':
            result = ConversionService.epsilon_nfa_to_dfa(data)
        elif conversion_type == 'nfa_to_epsilon_nfa':
            result = ConversionService.nfa_to_epsilon_nfa(data)
        else:
            result = {'error': 'Type de conversion non reconnu'}
        
        return jsonify(result)
    return render_template('conversions/epsilon_conversions.html')
