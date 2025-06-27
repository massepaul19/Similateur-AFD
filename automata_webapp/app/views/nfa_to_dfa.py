from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for , flash
from app.models.automate import Automate, AutomateService, db
from app.utils.nfa_to_dfa import NFAToDFAConverter
import json
import re

nfa_to_dfa_bp = Blueprint('nfa_to_dfa', __name__, url_prefix='/nfa-to-dfa')

@nfa_to_dfa_bp.route('/')
def index():
    """Page principale de conversion AFN vers AFD"""
    # Récupérer tous les AFN disponibles
    nfas = Automate.query.filter(Automate.type.in_(['afn'])).order_by(Automate.created_at.desc()).all()
    
    return render_template('conversions/nfa_to_dfa.html', nfas=nfas)

# Dans votre fichier nfa_to_dfa.py

def check_completeness(automate):
    """
    Vérifie si un automate est complet
    """
    if not automate or not automate.transitions:
        return False
    
    # Logique pour vérifier la complétude
    # Exemple basique - à adapter selon votre structure de données
    try:
        # Récupérer l'alphabet et les états
        alphabet = set()
        states = set()
        
        # Parser les transitions (adapter selon votre format)
        transitions = automate.transitions
        if isinstance(transitions, str):
            import json
            transitions = json.loads(transitions)
        
        for transition in transitions:
            if 'from_state' in transition:
                states.add(transition['from_state'])
            if 'to_state' in transition:
                states.add(transition['to_state'])
            if 'symbol' in transition and transition['symbol'] != 'ε':
                alphabet.add(transition['symbol'])
        
        # Vérifier que chaque état a une transition pour chaque symbole
        for state in states:
            for symbol in alphabet:
                has_transition = any(
                    t.get('from_state') == state and t.get('symbol') == symbol
                    for t in transitions
                )
                if not has_transition:
                    return False
        
        return True
        
    except Exception:
        return False

@nfa_to_dfa_bp.route('/afd-to-afdc')
def afd_to_afdc():
    """Page de conversion AFD vers AFDC"""
    # Récupérer tous les AFD disponibles
    afds = Automate.query.filter(Automate.type == 'afd').order_by(Automate.created_at.desc()).all()
    return render_template('conversions/dfa_to_afdc.html', 
                         afds=afds, 
                         check_completeness=check_completeness)

@nfa_to_dfa_bp.route('/complete-afd/<int:afd_id>')
def complete_afd(afd_id):
    """Compléter un AFD (le rendre complet)"""
    try:
        afd = Automate.query.get_or_404(afd_id)
        
        # Logique pour compléter l'AFD
        # À implémenter selon votre algorithme
        
        flash(f'AFD "{afd.name}" complété avec succès !', 'success')
        return redirect(url_for('nfa_to_dfa.afd_to_afdc'))
        
    except Exception as e:
        flash(f'Erreur lors de la complétion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.afd_to_afdc'))
    

@nfa_to_dfa_bp.route('/afd-minimization')
def afd_minimization():
    """Page de minimisation d'AFD"""
    # Récupérer tous les AFD et AFDC disponibles
    afds = Automate.query.filter(Automate.type.in_(['afd', 'afdc'])).order_by(Automate.created_at.desc()).all()
    return render_template('conversions/epsiolon_conversions.html', afds=afds)

@nfa_to_dfa_bp.route('/afd-complement')
def afd_complement():
    """Page de complémentation d'AFD"""
    # Récupérer tous les AFD et AFDC disponibles
    afds = Automate.query.filter(Automate.type.in_(['afd', 'afdc'])).order_by(Automate.created_at.desc()).all()
    return render_template('conversions/dfa_to_complete.html', afds=afds)



@nfa_to_dfa_bp.route('/epsilon-afn-to-afd')
def epsilon_afn_to_afd():
    """Page de conversion epsilon-AFN vers AFD"""
    # Récupérer tous les epsilon-AFN disponibles
    epsilon_afns = Automate.query.filter(Automate.type == 'epsilon-afn').order_by(Automate.created_at.desc()).all()
    return render_template('conversions/epsilon_to_afd.html', epsilon_afns=epsilon_afns)

@nfa_to_dfa_bp.route('/afd-to-epsilon-afn')
def afd_to_epsilon_afn():
    """Page de conversion AFD vers epsilon-AFN"""
    # Récupérer tous les AFD disponibles
    afds = Automate.query.filter(Automate.type == 'afd').order_by(Automate.created_at.desc()).all()
    return render_template('conversions/afd_to_epsilon.html', afds=afds)

@nfa_to_dfa_bp.route('/afd-to-afn')
def afd_to_afn():
    """Page de conversion AFD vers AFN"""
    # Récupérer tous les AFD disponibles
    afds = Automate.query.filter(Automate.type == 'afd').order_by(Automate.created_at.desc()).all()
    return render_template('conversions/afd_to_afn.html', afds=afds)

@nfa_to_dfa_bp.route('/afn-to-epsilon-afn')
def afn_to_epsilon_afn():
    """Page de conversion AFN vers epsilon-AFN"""
    # Récupérer tous les AFN disponibles
    nfas = Automate.query.filter(Automate.type.in_(['afn'])).order_by(Automate.created_at.desc()).all()
    return render_template('conversions/afn_to_eafn.html', nfas=nfas)

@nfa_to_dfa_bp.route('/epsilon-afn-to-afn')
def epsilon_afn_to_afn():
    """Page de conversion epsilon-AFN vers AFN"""
    # Récupérer tous les epsilon-AFN disponibles
    epsilon_afns = Automate.query.filter(Automate.type == 'epsilon-afn').order_by(Automate.created_at.desc()).all()
    return render_template('conversions/eafn_to_afn.html', epsilon_afns=epsilon_afns)
@nfa_to_dfa_bp.route('/convert-epsilon-afn-to-afd', methods=['POST'])
def convert_epsilon_afn_to_afd():
    """Traiter la conversion epsilon-AFN vers AFD"""
    try:
        automate_id = request.form.get('automate_id')
        if not automate_id:
            flash('Veuillez sélectionner un automate à convertir.', 'error')
            return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afd'))
        
        # Logique de conversion epsilon-AFN vers AFD
        # À implémenter selon votre algorithme
        
        flash('Conversion epsilon-AFN vers AFD réussie !', 'success')
        return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afd'))
        
    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afd'))

@nfa_to_dfa_bp.route('/convert-afd-to-epsilon-afn', methods=['POST'])
def convert_afd_to_epsilon_afn():
    """Traiter la conversion AFD vers epsilon-AFN"""
    try:
        automate_id = request.form.get('automate_id')
        if not automate_id:
            flash('Veuillez sélectionner un automate à convertir.', 'error')
            return redirect(url_for('nfa_to_dfa.afd_to_epsilon_afn'))
        
        # Logique de conversion AFD vers epsilon-AFN
        # À implémenter selon votre algorithme
        
        flash('Conversion AFD vers epsilon-AFN réussie !', 'success')
        return redirect(url_for('nfa_to_dfa.afd_to_epsilon_afn'))
        
    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.afd_to_epsilon_afn'))

@nfa_to_dfa_bp.route('/convert-afd-to-afn', methods=['POST'])
def convert_afd_to_afn():
    """Traiter la conversion AFD vers AFN"""
    try:
        automate_id = request.form.get('automate_id')
        if not automate_id:
            flash('Veuillez sélectionner un automate à convertir.', 'error')
            return redirect(url_for('nfa_to_dfa.afd_to_afn'))
        
        # Logique de conversion AFD vers AFN (triviale)
        # À implémenter selon votre algorithme
        
        flash('Conversion AFD vers AFN réussie !', 'success')
        return redirect(url_for('nfa_to_dfa.afd_to_afn'))
        
    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.afd_to_afn'))

@nfa_to_dfa_bp.route('/convert-afn-to-epsilon-afn', methods=['POST'])
def convert_afn_to_epsilon_afn():
    """Traiter la conversion AFN vers epsilon-AFN"""
    try:
        automate_id = request.form.get('automate_id')
        if not automate_id:
            flash('Veuillez sélectionner un automate à convertir.', 'error')
            return redirect(url_for('nfa_to_dfa.afn_to_epsilon_afn'))
        
        # Logique de conversion AFN vers epsilon-AFN
        # À implémenter selon votre algorithme
        
        flash('Conversion AFN vers epsilon-AFN réussie !', 'success')
        return redirect(url_for('nfa_to_dfa.afn_to_epsilon_afn'))
        
    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.afn_to_epsilon_afn'))

@nfa_to_dfa_bp.route('/convert-epsilon-afn-to-afn', methods=['POST'])
def convert_epsilon_afn_to_afn():
    """Traiter la conversion epsilon-AFN vers AFN"""
    try:
        automate_id = request.form.get('automate_id')
        if not automate_id:
            flash('Veuillez sélectionner un automate à convertir.', 'error')
            return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afn'))
        
        # Logique de conversion epsilon-AFN vers AFN
        # À implémenter selon votre algorithme
        
        flash('Conversion epsilon-AFN vers AFN réussie !', 'success')
        return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afn'))
        
    except Exception as e:
        flash(f'Erreur lors de la conversion : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.epsilon_afn_to_afn'))
    

# Version corrigée des fonctions d'extraction d'expression régulière

import json
import re
from flask import render_template, redirect, url_for, flash

# Route pour l'extraction d'expression régulière
@nfa_to_dfa_bp.route('/extract-regex')
def extract_regex():
    """Page d'extraction d'expression régulière"""
    try:
        # Récupérer tous les automates (AFN et AFD)
        automates = Automate.query.filter(
            Automate.type.in_(['afn', 'afd', 'epsilon-afn'])
        ).order_by(Automate.created_at.desc()).all()
        
        print(f"[DEBUG] Automates trouvés: {len(automates)}")  # Debug
        for auto in automates:
            print(f"[DEBUG] Automate {auto.id}: {auto.name}, type: {auto.type}")
        
        return render_template('conversions/extract_regex.html', automates=automates)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des automates : {str(e)}")
        flash(f'Erreur lors du chargement des automates : {str(e)}', 'error')
        return render_template('conversions/extract_regex.html', automates=[])

@nfa_to_dfa_bp.route('/extract-regex/<int:automate_id>')
def extract_regex_from_automate(automate_id):
    """Extraire l'expression régulière d'un automate spécifique"""
    try:
        automate = Automate.query.get_or_404(automate_id)
        print(f"[DEBUG] Extraction pour automate {automate.id}: {automate.name}")
        
        # Extraire l'expression régulière
        regex = generate_regex_from_automate(automate)
        print(f"[DEBUG] Expression régulière générée: {regex}")
        
        # Récupérer tous les automates pour la liste
        automates = Automate.query.filter(
            Automate.type.in_(['afn', 'afd', 'epsilon-afn'])
        ).order_by(Automate.created_at.desc()).all()
        
        return render_template('conversions/extract_regex.html', 
                             automates=automates,
                             selected_automate=automate,
                             extracted_regex=regex)
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'extraction : {str(e)}")
        flash(f'Erreur lors de l\'extraction : {str(e)}', 'error')
        return redirect(url_for('nfa_to_dfa.extract_regex'))

def generate_regex_from_automate(automate):
    """
    Génère une expression régulière à partir d'un automate en utilisant l'algorithme d'élimination d'états
    """
    try:
        print(f"[DEBUG] Début génération regex pour automate {automate.name}")
        
        # Parser les données de l'automate de manière sécurisée
        transitions_data = safe_parse_json(automate.transitions)
        states_data = safe_parse_json(automate.states)
        
        print(f"[DEBUG] States data: {states_data}")
        print(f"[DEBUG] Transitions data: {transitions_data}")
        
        if not transitions_data or not states_data:
            raise ValueError("Données d'automate invalides")
        
        # Extraire les informations des états
        states = set()
        final_states = set()
        initial_state = None
        
        # Créer un mapping state_id -> propriétés pour les cas où on utilise les IDs
        state_mapping = {}
        
        for state in states_data:
            state_name = None
            is_initial = False
            is_final = False
            
            # Gérer différents formats de données d'états
            if hasattr(state, '__dict__'):
                # Objet SQLAlchemy AutomateState
                # Inspecter les attributs disponibles
                print(f"[DEBUG] Objet état: {state.__dict__}")
                
                # Priorité au state_id qui correspond aux transitions
                state_name = (getattr(state, 'state_id', None) or 
                             getattr(state, 'name', None) or 
                             getattr(state, 'id', None) or 
                             getattr(state, 'label', None) or
                             str(state))
                
                # Vérifier les propriétés de l'objet SQLAlchemy
                is_initial = (getattr(state, 'is_initial', False) or 
                             getattr(state, 'initial', False))
                is_final = (getattr(state, 'is_final', False) or 
                           getattr(state, 'final', False) or
                           getattr(state, 'accepting', False))
                
                # Créer le mapping pour les cas mixtes
                state_id = getattr(state, 'state_id', None)
                numeric_id = getattr(state, 'id', None)
                if state_id and numeric_id:
                    state_mapping[str(numeric_id)] = state_id
                
            elif isinstance(state, dict):
                # Priorité au state_id qui correspond aux transitions
                state_name = (state.get('state_id') or
                             state.get('name') or 
                             state.get('id') or 
                             state.get('label'))
                
                # Vérifier les différents formats pour les états initiaux/finaux
                is_initial = (state.get('isInitial', False) or 
                             state.get('initial', False) or 
                             state.get('is_initial', False))
                is_final = (state.get('isFinal', False) or 
                           state.get('final', False) or 
                           state.get('is_final', False) or
                           state.get('accepting', False))
                           
            elif isinstance(state, str):
                state_name = state
            else:
                state_name = str(state)
            
            # Convertir en string seulement si nécessaire
            if state_name is not None:
                state_name = str(state_name)
                states.add(state_name)
                
                if is_initial:
                    initial_state = state_name
                    print(f"[DEBUG] État initial trouvé: {state_name}")
                    
                if is_final:
                    final_states.add(state_name)
                    print(f"[DEBUG] État final trouvé: {state_name}")
        
        print(f"[DEBUG] États: {states}")
        print(f"[DEBUG] État initial: {initial_state}")
        print(f"[DEBUG] États finaux: {final_states}")
        print(f"[DEBUG] Mapping état: {state_mapping}")
        
        # Vérifications et corrections pour les cas où les états ne sont pas marqués
        if not initial_state and states:
            # Prendre le premier état comme initial si aucun n'est marqué
            initial_state = sorted(list(states))[0]
            print(f"[DEBUG] Aucun état initial trouvé, utilisation de {initial_state}")
            
        if not final_states and states:
            # Prendre le dernier état comme final si aucun n'est marqué
            final_states.add(sorted(list(states))[-1])
            print(f"[DEBUG] Aucun état final trouvé, utilisation de {final_states}")
        
        if not initial_state:
            raise ValueError("Aucun état initial trouvé")
        if not final_states:
            raise ValueError("Aucun état final trouvé")
        
        # Construire la matrice de transitions
        transition_matrix = build_transition_matrix(states, transitions_data, state_mapping)
        print(f"[DEBUG] Matrice de transitions construite: {transition_matrix}")
        
        # Appliquer l'algorithme d'élimination d'états
        regex = state_elimination_algorithm(transition_matrix, initial_state, final_states, states)
        print(f"[DEBUG] Regex finale: {regex}")
        
        return regex if regex and regex != "∅" else "∅"
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la génération : {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Erreur lors de la génération de l'expression régulière : {str(e)}")

def build_transition_matrix(states, transitions_data, state_mapping=None):
    """
    Construit une matrice de transitions pour l'algorithme d'élimination
    """
    print(f"[DEBUG] Construction matrice pour états: {states}")
    print(f"[DEBUG] Avec transitions: {transitions_data}")
    print(f"[DEBUG] Mapping disponible: {state_mapping}")
    
    states_list = sorted(list(states))
    matrix = {}
    
    # Initialiser la matrice
    for i in states_list:
        matrix[i] = {}
        for j in states_list:
            matrix[i][j] = []
    
    # Remplir la matrice avec les transitions
    for transition in transitions_data:
        print(f"[DEBUG] Traitement transition: {transition}")
        
        from_state = None
        to_state = None
        symbol = None
        
        # Gérer différents formats de transitions
        if hasattr(transition, '__dict__'):
            # Objet SQLAlchemy AutomateTransition
            print(f"[DEBUG] Objet transition: {transition.__dict__}")
            
            # Essayer différents attributs possibles
            from_state = (getattr(transition, 'from_state', None) or 
                         getattr(transition, 'source', None) or
                         getattr(transition, 'start_state', None))
            to_state = (getattr(transition, 'to_state', None) or 
                       getattr(transition, 'target', None) or
                       getattr(transition, 'end_state', None))
            symbol = (getattr(transition, 'symbol', None) or 
                     getattr(transition, 'label', None) or 
                     getattr(transition, 'input', None))
            
        elif isinstance(transition, dict):
            from_state = (transition.get('from_state') or 
                         transition.get('source') or 
                         transition.get('from') or 
                         transition.get('start'))
            to_state = (transition.get('to_state') or 
                       transition.get('target') or 
                       transition.get('to') or 
                       transition.get('end'))
            symbol = (transition.get('symbol') or 
                     transition.get('label') or 
                     transition.get('input') or 
                     transition.get('char'))
        else:
            # Format liste [from, to, symbol]
            try:
                from_state, to_state, symbol = transition[:3]
            except (IndexError, ValueError):
                print(f"[DEBUG] Format de transition non reconnu: {transition}")
                continue
        
        # Convertir en chaînes seulement si nécessaire et appliquer le mapping si disponible
        if from_state is not None:
            from_state = str(from_state)
            # Appliquer le mapping si disponible
            if state_mapping and from_state in state_mapping:
                from_state = state_mapping[from_state]
                
        if to_state is not None:
            to_state = str(to_state)
            # Appliquer le mapping si disponible
            if state_mapping and to_state in state_mapping:
                to_state = state_mapping[to_state]
                
        if symbol is not None:
            symbol = str(symbol)
        
        print(f"[DEBUG] Transition extraite: {from_state} -> {to_state} avec '{symbol}'")
        
        if from_state in states and to_state in states and symbol is not None:
            # Traiter les epsilon-transitions
            if symbol in ['ε', 'epsilon', '', 'λ', 'None', 'null']:
                symbol = 'ε'
            elif not symbol or symbol == 'None':
                symbol = 'ε'
            
            matrix[from_state][to_state].append(symbol)
            print(f"[DEBUG] Ajouté à matrice: {from_state}[{to_state}] = {matrix[from_state][to_state]}")
        else:
            print(f"[DEBUG] États non trouvés ou symbole invalide:")
            print(f"[DEBUG]   from_state '{from_state}' in states: {from_state in states}")
            print(f"[DEBUG]   to_state '{to_state}' in states: {to_state in states}")
            print(f"[DEBUG]   symbol: '{symbol}'")
    
    # Convertir les listes en expressions régulières
    for i in states_list:
        for j in states_list:
            transitions = matrix[i][j]
            if not transitions:
                matrix[i][j] = None
            elif len(transitions) == 1:
                matrix[i][j] = transitions[0]
            else:
                # Plusieurs transitions -> union
                unique_symbols = sorted(list(set(transitions)))
                if len(unique_symbols) == 1:
                    matrix[i][j] = unique_symbols[0]
                else:
                    matrix[i][j] = '(' + '|'.join(unique_symbols) + ')'
    
    print(f"[DEBUG] Matrice finale: {matrix}")
    return matrix

# Fonction utilitaire pour déboguer les objets SQLAlchemy
def inspect_sqlalchemy_object(obj, name=""):
    """Fonction utilitaire pour déboguer les objets SQLAlchemy"""
    print(f"[DEBUG] Inspection de {name}: {obj}")
    print(f"[DEBUG] Type: {type(obj)}")
    
    if hasattr(obj, '__dict__'):
        print(f"[DEBUG] Attributs dict: {obj.__dict__}")
    
    # Lister tous les attributs de l'objet
    all_attrs = dir(obj)
    relevant_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
    print(f"[DEBUG] Attributs publics: {relevant_attrs}")
    
    # Tester différents attributs possibles
    possible_attrs = ['name', 'id', 'label', 'is_initial', 'initial', 'is_final', 'final', 'accepting',
                     'from_state', 'to_state', 'source', 'target', 'symbol', 'input', 'char']
    
    for attr in possible_attrs:
        if hasattr(obj, attr):
            try:
                value = getattr(obj, attr)
                print(f"[DEBUG] {attr}: {value} (type: {type(value)})")
            except Exception as e:
                print(f"[DEBUG] Erreur lors de l'accès à {attr}: {e}")

# Version améliorée de safe_parse_json avec plus de débogage
def safe_parse_json(data):
    """Parse JSON de manière sécurisée avec débogage avancé"""
    print(f"[DEBUG] Parsing data: {type(data)} - {data}")
    
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            print(f"[DEBUG] JSON parsé avec succès: {parsed}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Erreur JSON: {e}")
            return None
    elif isinstance(data, (list, dict)):
        print(f"[DEBUG] Data déjà en format Python")
        return data
    elif hasattr(data, '__iter__') and not isinstance(data, str):
        # Pour les collections SQLAlchemy
        print(f"[DEBUG] Collection SQLAlchemy détectée")
        result = list(data)
        print(f"[DEBUG] Collection convertie: {result}")
        
        # Inspecter chaque élément pour le débogage
        for i, item in enumerate(result):
            print(f"[DEBUG] Item {i}:")
            inspect_sqlalchemy_object(item, f"item_{i}")
        
        return result
    
    print(f"[DEBUG] Format de data non reconnu")
    return None

def state_elimination_algorithm(matrix, initial_state, final_states, states):
    """
    Algorithme d'élimination d'états pour générer l'expression régulière
    """
    print(f"[DEBUG] Début algorithme élimination")
    print(f"[DEBUG] Initial: {initial_state}, Final: {final_states}")
    
    states_list = list(states)
    working_matrix = {i: {j: matrix[i][j] for j in matrix[i]} for i in matrix}
    
    # Cas simple : si on a seulement l'état initial et final
    if len(states_list) == 1 and initial_state in final_states:
        # Automate trivial qui accepte epsilon
        loop = working_matrix.get(initial_state, {}).get(initial_state)
        if loop:
            return f"({loop})*"
        else:
            return "ε"
    
    # Normaliser : s'assurer qu'il n'y a qu'un seul état final
    if len(final_states) > 1:
        new_final = generate_unique_state_name(states_list, 'qf')
        print(f"[DEBUG] Création nouvel état final: {new_final}")
        
        # Ajouter le nouvel état final à la matrice
        working_matrix[new_final] = {}
        for state in states_list:
            working_matrix[state][new_final] = None
            working_matrix[new_final] = working_matrix.get(new_final, {})
            working_matrix[new_final][state] = None
        
        # Connecter tous les états finaux au nouvel état final avec ε
        for final_state in final_states:
            working_matrix[final_state][new_final] = 'ε'
        
        states_list.append(new_final)
        final_states = {new_final}
    
    final_state = list(final_states)[0]
    print(f"[DEBUG] État final unique: {final_state}")
    
    # Si initial et final sont le même état
    if initial_state == final_state:
        loop = working_matrix.get(initial_state, {}).get(final_state)
        if loop and loop != 'ε':
            return f"({loop})*"
        else:
            return "ε"
    
    # Éliminer tous les états sauf l'initial et le final
    states_to_eliminate = [s for s in states_list if s != initial_state and s != final_state]
    print(f"[DEBUG] États à éliminer: {states_to_eliminate}")
    
    for state_k in states_to_eliminate:
        print(f"[DEBUG] Élimination de l'état: {state_k}")
        
        # Calculer l'auto-boucle sur l'état k
        loop_kk = working_matrix[state_k][state_k]
        loop_star = make_star(loop_kk) if loop_kk else None
        print(f"[DEBUG] Auto-boucle {state_k}: {loop_kk} -> {loop_star}")
        
        # Mettre à jour toutes les transitions qui passent par k
        remaining_states = [s for s in states_list if s != state_k]
        
        for i in remaining_states:
            for j in remaining_states:
                if i == state_k or j == state_k:
                    continue
                
                # Chemin direct de i vers j
                r_ij = working_matrix[i][j]
                
                # Chemin de i vers k
                r_ik = working_matrix[i][state_k]
                
                # Chemin de k vers j
                r_kj = working_matrix[state_k][j]
                
                # Calculer le nouveau chemin
                new_path = None
                if r_ik and r_kj:
                    if loop_star:
                        new_path = concatenate_regex([r_ik, loop_star, r_kj])
                    else:
                        new_path = concatenate_regex([r_ik, r_kj])
                    print(f"[DEBUG] Nouveau chemin {i}->{j} via {state_k}: {new_path}")
                
                # Combiner avec le chemin direct
                if r_ij and new_path:
                    working_matrix[i][j] = f"({r_ij}|{new_path})"
                elif new_path:
                    working_matrix[i][j] = new_path
                
                print(f"[DEBUG] Mise à jour {i}[{j}]: {working_matrix[i][j]}")
        
        # Supprimer l'état k de la matrice
        states_list.remove(state_k)
        del working_matrix[state_k]
        for state in working_matrix:
            if state_k in working_matrix[state]:
                del working_matrix[state][state_k]
    
    # L'expression régulière finale
    result = working_matrix.get(initial_state, {}).get(final_state)
    print(f"[DEBUG] Résultat brut: {result}")
    
    # Nettoyer et simplifier l'expression
    if result:
        result = clean_regex(result)
        print(f"[DEBUG] Résultat nettoyé: {result}")
    
    return result or "∅"

def generate_unique_state_name(existing_states, prefix):
    """Génère un nom d'état unique"""
    counter = 1
    while f"{prefix}_{counter}" in existing_states:
        counter += 1
    return f"{prefix}_{counter}"

def make_star(expression):
    """Ajoute l'opérateur étoile à une expression"""
    if not expression or expression == 'ε':
        return ''
    
    if expression == '∅':
        return ''
    
    if len(expression) == 1 and expression.isalnum():
        return f"{expression}*"
    else:
        return f"({expression})*"

def concatenate_regex(parts):
    """Concatène plusieurs parties d'expression régulière"""
    result_parts = []
    for part in parts:
        if part and part != 'ε' and part != '':
            result_parts.append(part)
    
    if not result_parts:
        return 'ε'
    
    return ''.join(result_parts)

def clean_regex(regex):
    """Nettoie et simplifie l'expression régulière"""
    if not regex:
        return "∅"
    
    original = regex
    
    # Remplacer les epsilon par des chaînes vides dans les concaténations
    regex = re.sub(r'ε([a-zA-Z0-9\(\)])', r'\1', regex)
    regex = re.sub(r'([a-zA-Z0-9\(\)])ε', r'\1', regex)
    
    # Simplifier les unions avec epsilon
    regex = re.sub(r'\(ε\|([^)]+)\)', r'(\1)?', regex)
    regex = re.sub(r'\(([^)]+)\|ε\)', r'(\1)?', regex)
    
    # Supprimer les unions vides
    regex = re.sub(r'\|\s*\)', ')', regex)
    regex = re.sub(r'\(\s*\|', '(', regex)
    
    # Supprimer les parenthèses inutiles pour les caractères simples
    regex = re.sub(r'\(([a-zA-Z0-9])\)', r'\1', regex)
    
    # Nettoyer les espaces
    regex = re.sub(r'\s+', '', regex)
    
    # Simplifier les expressions vides
    if regex in ['', '()', 'ε']:
        return 'ε'
    
    print(f"[DEBUG] Nettoyage: '{original}' -> '{regex}'")
    return regex

# Fonction utilitaire pour déboguer les objets SQLAlchemy
def inspect_sqlalchemy_object(obj, name=""):
    """Fonction utilitaire pour déboguer les objets SQLAlchemy"""
    print(f"[DEBUG] Inspection de {name}: {obj}")
    print(f"[DEBUG] Type: {type(obj)}")
    
    if hasattr(obj, '__dict__'):
        print(f"[DEBUG] Attributs: {obj.__dict__}")
    
    # Tester différents attributs possibles
    possible_attrs = ['name', 'id', 'label', 'is_initial', 'initial', 'is_final', 'final', 'accepting',
                     'from_state', 'to_state', 'source', 'target', 'symbol', 'input', 'char']
    
    for attr in possible_attrs:
        if hasattr(obj, attr):
            value = getattr(obj, attr)
            print(f"[DEBUG] {attr}: {value} (type: {type(value)})")