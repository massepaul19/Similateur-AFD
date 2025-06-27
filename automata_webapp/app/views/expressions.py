# ==================== app/views/expressions.py ====================
from flask import Blueprint, render_template, request, jsonify
from app.services.automaton_service import AutomatonService

expressions_bp = Blueprint('expressions', __name__)

@expressions_bp.route('/regex-to-automaton', methods=['GET', 'POST'])
def regex_to_automaton():
    """Conversion d'expression régulière vers automate"""
    if request.method == 'POST':
        data = request.get_json()
        algorithm = data.get('algorithm', 'thompson')  # thompson ou glushkov
        
        if algorithm == 'thompson':
            result = AutomatonService.thompson_construction(data['regex'])
        elif algorithm == 'glushkov':
            result = AutomatonService.glushkov_construction(data['regex'])
        else:
            result = {'error': 'Algorithme non reconnu'}
        
        return jsonify(result)
    return render_template('expressions/regex_to_automaton.html')

@expressions_bp.route('/automaton-to-regex', methods=['GET', 'POST'])
def automaton_to_regex():
    """Extraction d'expression régulière depuis un automate"""
    if request.method == 'POST':
        data = request.get_json()
        result = AutomatonService.extract_regex(data)
        return jsonify(result)
    return render_template('expressions/automaton_to_regex.html')

@expressions_bp.route('/system-solver', methods=['GET', 'POST'])
def system_solver():
    """Résolution de système d'équations"""
    if request.method == 'POST':
        data = request.get_json()
        result = AutomatonService.solve_equation_system(data['equations'])
        return jsonify(result)
    return render_template('expressions/system_solver.html')
