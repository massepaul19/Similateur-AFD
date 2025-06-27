from flask import Blueprint, render_template, request, jsonify
from app.services.automaton_service import AutomatonService
from app.services.minimisation import MinimizationService
from app.models.automate import Automate

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/state-analysis', methods=['GET', 'POST'])
def state_analysis():
    """Analyse des états (accessibles, co-accessibles, utiles)"""
    if request.method == 'POST':
        data = request.get_json()
        result = AutomatonService.analyze_states(data)
        return jsonify(result)
    return render_template('operations/state_analysis.html')
# Route principale de la minimisation avec blueprint renommé
@operations_bp.route('/')
def index():
    """Page principale de minimisation"""
    automates = Automate.query.filter(
                Automate.type.in_(['afn', 'afdc' , 'afd', 'epsilon-afn'])
            ).order_by(Automate.created_at.desc()).all()    # Filtrer pour ne garder que les AFDC
    afdc_automates = [a for a in automates if a.type == 'afdc' or a.type == 'afd']
    
    return render_template('operations/minimization.html', automates=afdc_automates)


@operations_bp.route('/minimize/<int:automate_id>')
def minimize(automate_id):
    """Minimiser un automate spécifique"""
    try:
        result = MinimizationService.minimize_automate(automate_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@operations_bp.route('/distinguish/<int:automate_id>')
def distinguish(automate_id):
    """Obtenir les séquences distinguantes"""
    try:
        result = MinimizationService.get_distinguishing_sequences(automate_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@operations_bp.route('/pruning', methods=['GET', 'POST'])
def pruning():
    """Émondage d'automate"""
    if request.method == 'POST':
        data = request.get_json()
        result = AutomatonService.prune_automaton(data)
        return jsonify(result)
    return render_template('operations/pruning.html')

@operations_bp.route('/closure-operations', methods=['GET', 'POST'])
def closure_operations():
    """Opérations de clôture (union, intersection, etc.)"""
    if request.method == 'POST':
        operations_type = request.json.get('operation')
        automata_data = request.json.get('automata')
        
        result = AutomatonService.perform_closure_operation(operations_type, automata_data)
        return jsonify(result)
    return render_template('operations/closure_ops.html')


@operations_bp.route('/systeme', methods=['GET'])
def my_automat():
    """Page listant tous les automates enregistrés"""
    # Tu peux plus tard charger les automates depuis une base ou un fichier
    return render_template('operations/solve_system.html')
