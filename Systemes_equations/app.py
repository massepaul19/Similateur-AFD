from flask import Flask, render_template, request, jsonify
import re
from typing import Dict, List, Set, Tuple

app = Flask(__name__)

class AutomatonSolver:
    def __init__(self):
        self.equations = {}
        self.solutions = {}
    
    def generate_equations_from_automaton(self, automaton_data):
        """Génère le système d'équations à partir de l'automate"""
        alphabet = automaton_data['alphabet']
        states = automaton_data['states']
        initial_states = automaton_data['initialStates']
        final_states = automaton_data['finalStates']
        transitions = automaton_data['transitions']
        
        equations = {}
        
        # Pour chaque état, créer l'équation
        for state in states:
            equation_parts = []
            
            # Ajouter epsilon si état final
            if state in final_states:
                equation_parts.append('ε')
            
            # Parcourir toutes les transitions possibles
            for symbol in alphabet:
                key = f"{state}_{symbol}"
                if key in transitions and transitions[key]:
                    for target_state in transitions[key]:
                        equation_parts.append(f"{symbol}X{target_state}")
            
            # Construire l'équation
            
            if equation_parts:
                equations[f"X{state}"] = " + ".join(equation_parts)
            else:
                equations[f"X{state}"] = "∅"
        
        return equations

########################################################################################    
    
    # Cette partie permet de definir le lemme d'arden i.e
    
    def apply_arden_lemma(self, variable, coefficient, other_terms):
    
        """Applique le lemme d'Arden: X = AX + B => X = A*B"""
        
        if coefficient and coefficient != "ε":
            if other_terms:
                return f"({coefficient})*({other_terms})"
            else:
                return f"({coefficient})*"
        else:
            return other_terms if other_terms else "ε"
    

########################################################################################


    def substitute_variable(self, equations, var_to_substitute, substitution):
        """Substitue une variable dans toutes les équations"""
        new_equations = {}
        
        for var, eq in equations.items():
            if var == var_to_substitute:
                continue
            
            # Remplacer la variable par sa substitution
            new_eq = eq.replace(var_to_substitute, f"({substitution})")
            new_equations[var] = self.simplify_expression(new_eq)
        
        return new_equations


########################################################################################

    def simplify_expression(self, expression):
        """Simplifie une expression régulière"""
        # Simplifications de base
        expression = expression.replace("(ε)", "ε")
        expression = expression.replace("ε + ", "")
        expression = expression.replace(" + ε", "")
        expression = re.sub(r'\s+', ' ', expression)
        
        return expression.strip()
    


########################################################################################

    def solve_system(self, equations):
        """Résout le système d'équations par substitution"""
        working_equations = equations.copy()
        solutions = {}
        step_by_step = []
        
        # Ordre de résolution (priorité aux équations sans récursion)
        variables = list(working_equations.keys())
        
        for variable in variables:
            equation = working_equations[variable]
            
            # Séparer les termes récursifs des autres
            recursive_terms = []
            other_terms = []
            
            # Analyser l'équation
            terms = equation.split(' + ')
            coefficient = ""
            
            for term in terms:
                if term.strip() == "ε":
                    other_terms.append(term.strip())
                elif variable in term:
                    # Terme récursif
                    coeff = term.replace(variable, '').strip()
                    if coeff:
                        coefficient = coeff
                else:
                    other_terms.append(term.strip())
            
            # Appliquer le lemme d'Arden si nécessaire
            
            if coefficient:
                other_part = " + ".join(other_terms) if other_terms else ""
                solution = self.apply_arden_lemma(variable, coefficient, other_part)
            else:
                solution = " + ".join(other_terms) if other_terms else "∅"
            
            solutions[variable] = solution
            step_by_step.append({
                'variable': variable,
                'equation': equation,
                'solution': solution,
                'method': 'Lemme d\'Arden' if coefficient else 'Substitution directe'
            })
            
            # Substituer dans les équations restantes
            
            remaining_vars = [v for v in variables if v != variable and v not in solutions]
            if remaining_vars:
                for var in remaining_vars:
                    if variable in working_equations[var]:
                        old_eq = working_equations[var]
                        working_equations[var] = old_eq.replace(variable, f"({solution})")
                        working_equations[var] = self.simplify_expression(working_equations[var])
        
        return solutions, step_by_step


########################################################################################

solver = AutomatonSolver()


########################################################################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_equations', methods=['POST'])
def generate_equations():
    try:
        automaton_data = request.json
        equations = solver.generate_equations_from_automaton(automaton_data)
        return jsonify({
            'success': True,
            'equations': equations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/solve_equations', methods=['POST'])
def solve_equations():
    try:
        data = request.json
        equations = data.get('equations', {})
        
        solutions, steps = solver.solve_system(equations)
        
        return jsonify({
            'success': True,
            'solutions': solutions,
            'steps': steps
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/manual_equations', methods=['POST'])
def manual_equations():
    try:
        data = request.json
        equations = data.get('equations', {})
        
        solutions, steps = solver.solve_system(equations)
        
        return jsonify({
            'success': True,
            'solutions': solutions,
            'steps': steps
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

#if __name__ == '__main__':
#    app.run(debug=True)
    
if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5001")
    print("🔗 Lien vers automates: http://localhost:5000")
    app.run(host='0.0.0.0', port=5001, debug=True)
