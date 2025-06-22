from flask import Flask, render_template, request, jsonify
import re
from typing import Dict, List, Set, Tuple
from utils import distribute_concatenation , simplify_expression

app = Flask(__name__)

class AutomatonSolver:
    def __init__(self):
        self.equations = {}
        self.solutions = {}
    

######################################################################################## 

   #Cette fonction me permet de generer un systeme directement a partir d'un automate
   
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
            
        return equations
        
########################################################################################    
    
    # Cette partie permet de definir le lemme d'arden i.e
    
    def apply_arden_lemma(self, variable, coefficient, other_terms):
        """Applique le lemme d'Arden: X = AX + B => X = A*B"""
        if coefficient and coefficient != "ε":
            if other_terms and other_terms != "":
                return f"({coefficient})*({other_terms})"
            else:
                return f"({coefficient})*"
        else:
            return other_terms if other_terms else "ε"
            
########################################################################################    
    

    def parse_equation(self, equation, variable):
        """Parse une équation pour extraire le coefficient de la variable et les autres termes"""
        terms = [term.strip() for term in equation.split(' + ')]
        coefficient = ""
        other_terms = []
        
        for term in terms:
            if variable in term:
                # Terme récursif - extraire le coefficient
                coeff = term.replace(variable, '').strip()
                if coeff == "":
                    coefficient = "ε"
                else:
                    coefficient = coeff
            else:
                other_terms.append(term)
        
        other_part = " + ".join(other_terms) if other_terms else ""
        return coefficient, other_part
        

########################################################################################    
    
    # Cette fonction me permet me permet de remplacer une dans d'autres equations EX: (1) dans (2) et (3)

    def substitute_in_equation(self, equation, variable, substitution):
        """Substitue une variable dans une équation"""
        # Remplacer toutes les occurrences de la variable
        if variable in equation:
            if substitution == "ε":
                # Si la substitution est ε, on peut simplifier
                new_equation = equation.replace(variable, "")
            else:
                new_equation = equation.replace(variable, f"({substitution})")
            return simplify_expression(new_equation)
        return equation

        
########################################################################################    
    
    # Cette fonction me permet de groupe les termes d'une équation 

    def group_terms_by_variable(self, equation, target_variable):
        """Groupe les termes d'une équation selon qu'ils contiennent la variable cible ou non"""
        terms = [term.strip() for term in equation.split(' + ') if term.strip()]
        
        recursive_terms = []
        other_terms = []
        
        for term in terms:
            if target_variable in term:
                recursive_terms.append(term)
            else:
                other_terms.append(term)
        
        # Extraire les coefficients des termes récursifs
        
        coefficients = []
        for term in recursive_terms:
            coeff = term.replace(target_variable, '').strip()
            if coeff == "":
                coefficients.append("ε")
            else:
                coefficients.append(coeff)
        
        # Combiner les coefficients
        
        if coefficients:
            if len(coefficients) == 1:
                combined_coeff = coefficients[0]
            else:
                combined_coeff = " + ".join(coefficients)
        else:
            combined_coeff = ""
        
        other_part = " + ".join(other_terms) if other_terms else ""
        
        return combined_coeff, other_part

######################################################################################## 
   
   #Cette fonction defini la priorité sur la valeur sur laquelle le lemme d'arden doit s'appliquer

    def variable_score(self, var, eq):
        score = 0
        if 'ε' in eq:
            score -= 10  
        score += eq.count('+')  
        deps = set(re.findall(r'X\d+', eq))
        score += len(deps)
        if not deps:
            score -= 1 
        return score        
        
######################################################################################## 
   
   #Fonction principale pour la résolution du sytem        

######################################################################################## 

    def solve_system(self, equations):
        """Résout le système d'équations par substitution selon l'algorithme décrit"""
        working_equations = equations.copy()
        solutions = {}
        step_by_step = []
        
        # Trier les variables par ordre numérique et priorité
        variables = sorted(
            working_equations.keys(),
            key=lambda var: self.variable_score(var, working_equations[var])
        )

        step_counter = 1
        
        for variable in variables:
            equation = working_equations[variable]
            
            # Analyser l'équation courante
            coefficient, other_terms = self.group_terms_by_variable(equation, variable)
            
            # Appliquer le lemme d'Arden si coefficient présent
            if coefficient and coefficient != "":
                solution = self.apply_arden_lemma(variable, coefficient, other_terms)
                method = "Lemme d'Arden"
                
                step_by_step.append({
                    'step': step_counter,
                    'variable': variable,
                    'equation': equation,
                    'solution': solution,
                    'method': method,
                    'description': f"Application du lemme d'Arden sur {variable}",
                    'details': f"{variable} = {coefficient}{variable} + {other_terms if other_terms else ''} → {variable} = {solution}"
                })
            else:
                solution = other_terms if other_terms else "ε"
                method = "Substitution directe"
                
                step_by_step.append({
                    'step': step_counter,
                    'variable': variable,
                    'equation': equation,
                    'solution': solution,
                    'method': method,
                    'description': f"Résolution directe de {variable}"
                })
  
  ###################################################################################### 
            
            # Nettoyer la solution immédiatement après Arden
  
  ################## 
            
            if solution == "()*ε" or solution == "()*":
                solution = "ε"
            elif solution and solution.endswith("*ε"):
                cleaned_solution = solution.replace("*ε", "*")
                step_by_step.append({
                    'step': step_counter + 0.1,
                    'method': "Élimination de ε",
                    'description': "ε est neutre par concaténation",
                    'variable': variable,
                    'before': solution,
                    'after': cleaned_solution
                })
                solution = cleaned_solution
  
  ##################
  
            elif solution and solution.endswith("*(ε)"):
                cleaned_solution = solution.replace("*(ε)", "*")
                step_by_step.append({
                    'step': step_counter + 0.1,
                    'method': "Élimination de ε",
                    'description': "ε est neutre par concaténation : A*(ε) = A*",
                    'variable': variable,
                    'before': solution,
                    'after': cleaned_solution
                })
                solution = cleaned_solution
  
  ##################
            
            if '(' in solution and '+' in solution and 'ε' in solution:
                solution_distribue = distribute_concatenation(solution)
                if solution_distribue != solution:
                    step_by_step.append({
                        'step': step_counter + 0.1,
                        'method': "Élimination de ε",
                        'description': "Distribution de la concaténation : A(B + ε) = AB + A",
                        'variable': variable,
                        'before': solution,
                        'after': solution_distribue
                })
                solution = solution_distribue
                
            solutions[variable] = solution
            step_counter += 1
            
  #################################################################################### 
        
       # Substituer dans TOUTES les équations restantes (non résolues)

   ##################
  
            remaining_equations = {k: v for k, v in working_equations.items() if k not in solutions}
            
            if remaining_equations:
                substitution_step = {
                    'step': step_counter,
                    'method': "Substitution",
                    'description': f"Substitution de {variable} = {solution} dans toutes les équations restantes",
                    'substitutions': []
                }
                
                # Substituer dans chaque équation restante
                for var, eq in remaining_equations.items():
                    if variable in eq:
                        old_eq = eq
                        new_eq = self.substitute_in_equation(eq, variable, solution)
                        
                        substitution_step['substitutions'].append({
                            'variable': var,
                            'before': old_eq,
                            'after': new_eq
                        })
                        
                        # Mettre à jour l'équation dans working_equations
                        working_equations[var] = new_eq
                
                if substitution_step['substitutions']:
                    step_by_step.append(substitution_step)
                    step_counter += 1
        
        # ÉTAPE FINALE: Substitution complète pour obtenir des solutions indépendantes
        final_solutions = solutions.copy()
        
        # Ordre de substitution : du plus complexe au plus simple
        substitution_order = sorted(solutions.keys(), key=lambda x: len(solutions[x]), reverse=True)
        
        for var in substitution_order:
            current_solution = final_solutions[var]
            
            # Substituer toutes les autres variables dans cette solution
            for other_var in solutions:
                if other_var != var and other_var in current_solution:
                    current_solution = self.substitute_in_equation(current_solution, other_var, final_solutions[other_var])
            
            final_solutions[var] = current_solution
        
        # Étape finale d'affichage
        final_step = {
            'step': 'Final',
            'method': 'Substitution finale complète',
            'description': 'Obtention des solutions complètement indépendantes',
            'final_solutions': final_solutions
        }
        
        step_by_step.append(final_step)
        
        return final_solutions, step_by_step

######################################################################################## 
   

    def substitute_variable(self, equations, var_to_substitute, substitution):
        """Substitue une variable dans toutes les équations"""
        new_equations = {}
        
        for var, eq in equations.items():
            if var == var_to_substitute:
                continue
            
            # Remplacer la variable par sa substitution
            new_eq = self.substitute_in_equation(eq, var_to_substitute, substitution)
            new_equations[var] = new_eq
        
        return new_equations
        
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

if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
