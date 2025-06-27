from flask import Blueprint, render_template, request, jsonify
from app.services.visualization_service import VisualizationService

visualizations_bp = Blueprint('visualizations', __name__)

@visualizations_bp.route('/display', methods=['GET', 'POST'])
def display_automaton():
    """Affichage graphique d'un automate"""
    if request.method == 'POST':
        data = request.get_json()
        result = VisualizationService.generate_graph(data)
        return jsonify(result)
    return render_template('visualizations/automaton_display.html')

@visualizations_bp.route('/comparison', methods=['GET', 'POST'])
def compare_automata():
    """Comparaison visuelle de deux automates"""
    if request.method == 'POST':
        data = request.get_json()
        result = VisualizationService.compare_automata(data['automaton1'], data['automaton2'])
        return jsonify(result)
    return render_template('visualizations/comparison.html')

@visualizations_bp.route('/step-by-step', methods=['GET', 'POST'])
def step_by_step():
    """Visualisation étape par étape d'un algorithme"""
    if request.method == 'POST':
        data = request.get_json()
        algorithm = data.get('algorithm')
        result = VisualizationService.generate_step_by_step(algorithm, data)
        return jsonify(result)
    return render_template('visualizations/step_by_step.html')
