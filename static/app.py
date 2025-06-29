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
####################

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
####################    

    def variable_score(self, var, eq):
        """
        Calcule un score de priorité pour déterminer l'ordre de résolution.
        Plus le score est bas, plus la variable est prioritaire.
        """
        score = 0
        
        # Vérifier si la variable a un terme récursif direct
        has_recursive_term = var in eq
        
        if has_recursive_term:
            # Priorité haute pour les variables avec terme récursif
            score = 1
            
            # Analyser le coefficient du terme récursif
            coefficient, other_terms = self.group_terms_by_variable(eq, var)
            
            # Si le coefficient est simple (une lettre), priorité encore plus haute
            if coefficient and len(coefficient) == 1 and coefficient.isalpha():
                score = 0  # Priorité maximale
            
            # Pénalité si beaucoup d'autres variables dans les autres termes
            other_vars = set(re.findall(r'X\d+', other_terms)) if other_terms else set()
            score += len(other_vars) * 0.1
            
        else:
            # Variables sans terme récursif ont une priorité plus basse
            score = 10
            
            # Bonus si l'équation contient ε (souvent plus simple à résoudre)
            if 'ε' in eq:
                score = 5
            
            # Pénalité selon le nombre de variables dépendantes
            deps = set(re.findall(r'X\d+', eq))
            score += len(deps)
        
        return score

  ###################################################################################### 
            
            # Nettoyer la solution immédiatement après Arden
  
  ################## 

    def clean_solution(self, solution, step_by_step, step_counter):
        """Nettoie une solution en éliminant les ε inutiles"""
        if solution == "()*ε" or solution == "()*":
            return "ε"
        elif solution and solution.endswith("*ε"):
            cleaned_solution = solution.replace("*ε", "*")
            step_by_step.append({
                'step': step_counter + 0.1,
                'method': "Élimination de ε",
                'description': "ε est neutre par concaténation",
                'before': solution,
                'after': cleaned_solution
            })
            return cleaned_solution
        elif solution and solution.endswith("*(ε)"):
            cleaned_solution = solution.replace("*(ε)", "*")
            step_by_step.append({
                'step': step_counter + 0.1,
                'method': "Élimination de ε",
                'description': "ε est neutre par concaténation : A*(ε) = A*",
                'before': solution,
                'after': cleaned_solution
            })
            return cleaned_solution
        
        return solution

    def has_variables(self, expression):
        """Vérifie si une expression contient encore des variables X"""
        return bool(re.search(r'X\d+', expression))

  ###################################################################################### 
            
      # ici j'effectue les substitutions jusqu'à obtenir un result n'ayant pas de var
  
  ################## 
  
    def perform_final_substitutions(self, solutions, step_by_step, start_step):
        """Effectue les substitutions finales jusqu'à élimination complète des variables"""
        final_solutions = solutions.copy()
        step_counter = start_step
        max_iterations = 20  # Protection contre les boucles infinies
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            has_changes = False
            
            # Pour chaque solution, vérifier s'il y a encore des variables à substituer
            for var in list(final_solutions.keys()):
                current_solution = final_solutions[var]
                
                # Trouver toutes les variables dans cette solution
                variables_in_solution = re.findall(r'X\d+', current_solution)
                
                if variables_in_solution:
                    old_solution = current_solution
                    
                    # Substituer chaque variable trouvée
                    for other_var in variables_in_solution:
                        if other_var in final_solutions and other_var != var:
                            current_solution = self.substitute_in_equation(
                                current_solution, other_var, final_solutions[other_var]
                            )
                    
                    # Si la solution a changé, l'enregistrer
                    if current_solution != old_solution:
                        final_solutions[var] = current_solution
                        has_changes = True
                        
                        # Nettoyer la solution
                        cleaned_solution = self.clean_solution(current_solution, step_by_step, step_counter)
                        if cleaned_solution != current_solution:
                            final_solutions[var] = cleaned_solution
                        
                        step_by_step.append({
                            'step': step_counter,
                            'method': 'Substitution finale',
                            'description': f'Substitution des variables dans {var}',
                            'variable': var,
                            'before': old_solution,
                            'after': final_solutions[var]
                        })
                        
                        step_counter += 0.1
            
            # Si aucun changement n'a été effectué, on peut s'arrêter
            if not has_changes:
                break
        
        return final_solutions, step_by_step

######################################################################################## 
   
   #Fonction principale pour la résolution du sytem        

######################################################################################## 

    def solve_system_with_priority(self, equations):
        """
        Version améliorée qui résout d'abord les variables avec termes récursifs simples
        et effectue les substitutions finales complètes
        """
        working_equations = equations.copy()
        solutions = {}
        step_by_step = []
        step_counter = 1
        
        while working_equations:
            # Recalculer les priorités à chaque itération
            variables_scores = []
            for var in working_equations:
                score = self.variable_score(var, working_equations[var])
                variables_scores.append((score, var))
            
            # Trier par score (priorité)
            variables_scores.sort()
            
            # Prendre la variable la plus prioritaire
            _, variable = variables_scores[0]
            equation = working_equations[variable]
            
            print(f"Résolution de {variable}: {equation} (score: {variables_scores[0][0]})")
            
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
            
            # Nettoyer la solution
            solution = self.clean_solution(solution, step_by_step, step_counter)
            
            solutions[variable] = solution
            
            # Retirer cette variable du système
            del working_equations[variable]
            
            # Substituer dans toutes les équations restantes
            if working_equations:
                substitution_step = {
                    'step': step_counter + 0.5,
                    'method': "Substitution",
                    'description': f"Substitution de {variable} = {solution} dans toutes les équations restantes",
                    'substitutions': []
                }
                
                for var, eq in working_equations.items():
                    if variable in eq:
                        old_eq = eq
                        new_eq = self.substitute_in_equation(eq, variable, solution)
                        
                        substitution_step['substitutions'].append({
                            'variable': var,
                            'before': old_eq,
                            'after': new_eq
                        })
                        
                        working_equations[var] = new_eq
                
                if substitution_step['substitutions']:
                    step_by_step.append(substitution_step)
            
            step_counter += 1
        
        # ÉTAPE CRUCIALE: Substitutions finales complètes
        print("Début des substitutions finales...")
        final_solutions, step_by_step = self.perform_final_substitutions(
            solutions, step_by_step, step_counter
        )
        
        # Vérifier s'il reste encore des variables
        remaining_vars = []
        for var, sol in final_solutions.items():
            if self.has_variables(sol):
                remaining_vars.append(f"{var}: {sol}")
        
        if remaining_vars:
            print(f"ATTENTION: Variables restantes dans les solutions: {remaining_vars}")
        
        # Étape finale d'affichage
        final_step = {
            'step': 'Final',
            'method': 'Solutions finales complètes',
            'description': 'Solutions sans variables interdépendantes',
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
        
        solutions, steps = solver.solve_system_with_priority(equations)
        
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
        
        solutions, steps = solver.solve_system_with_priority(equations)
        
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
