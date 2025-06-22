import re
from typing import Dict, List, Tuple

class StrategicAutomatonSolver:
    
    def __init__(self):
        self.debug = True
    
    def parse_equation(self, equation: str, variable: str) -> Tuple[str, List[str]]:
        equation = equation.replace(" ", "")
        terms = self._split_terms(equation)
        recursive_coeff = ""
        other_terms = []
        for term in terms:
            if self._contains_variable(term, variable):
                coeff = term.replace(variable, "")
                recursive_coeff = coeff if coeff else "ε"
            else:
                other_terms.append(term)
        return recursive_coeff, other_terms
    
    def _split_terms(self, expression: str) -> List[str]:
        terms = []
        current = ""
        paren_count = 0
        for c in expression:
            if c == '(':
                paren_count += 1
            elif c == ')':
                paren_count -= 1
            if c == '+' and paren_count == 0:
                terms.append(current)
                current = ""
            else:
                current += c
        if current:
            terms.append(current)
        return terms

    def _contains_variable(self, term: str, variable: str) -> bool:
        pattern = r'\b' + re.escape(variable) + r'\b'
        return bool(re.search(pattern, term))

    def apply_arden_lemma(self, coeff: str, other_terms: List[str]) -> str:
        if not other_terms or (len(other_terms) == 1 and other_terms[0] == "ε"):
            return f"({coeff})*" if coeff != "ε" else "ε*"
        else:
            other = "+".join(other_terms)
            return f"({coeff})*({other})" if coeff != "ε" else other

    def substitute_variable(self, expr: str, var: str, subst: str) -> str:
        pattern = r'\b' + re.escape(var) + r'\b'
        result = re.sub(pattern, f"({subst})", expr)
        return self.simplify_expression(result)

    def simplify_expression(self, expr: str) -> str:
        expr = expr.replace(" ", "")
        expr = expr.replace("ε*", "")
        expr = expr.replace("(ε)", "ε")
        expr = expr.replace("ε+", "")
        expr = expr.replace("+ε", "")
        expr = expr.strip('+')
        expr = re.sub(r'\(\)', '', expr)
        if expr.startswith("(") and expr.endswith(")") and self._balanced_parentheses(expr[1:-1]):
            expr = expr[1:-1]
        return expr if expr else "ε"

    def _balanced_parentheses(self, expr: str) -> bool:
        count = 0
        for c in expr:
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0

    def has_recursion(self, equation: str, variable: str) -> bool:
        recursive_coeff, _ = self.parse_equation(equation, variable)
        return bool(recursive_coeff)

    def find_recursive_variables(self, equations: Dict[str, str]) -> List[str]:
        recursive_vars = []
        for var, eq in equations.items():
            if self.has_recursion(eq, var):
                recursive_vars.append(var)
        def dependency_count(var):
            eq = equations[var]
            return sum(1 for v in equations if v != var and self._contains_variable(eq, v))
        recursive_vars.sort(key=dependency_count)
        return recursive_vars

    def solve_system(self, equations: Dict[str, str]) -> Dict[str, str]:
        if self.debug:
            print("=" * 80)
            print("=== SYSTÈME INITIAL ===")
            for var, eq in equations.items():
                print(f"{var} = {eq}")

        solutions = {}
        working = equations.copy()

        recursive_vars = self.find_recursive_variables(working)
        if self.debug:
            print(f"\n=== VARIABLES RÉCURSIVES DÉTECTÉES ===")
            print(f"Variables avec récursion: {recursive_vars}")

        step = 1
        for var in recursive_vars:
            if self.debug:
                print(f"\n=== ÉTAPE {step}: Application du lemme d'Arden sur {var} ===")
                step += 1
                print(f"Équation: {var} = {working[var]}")
            coeff, other_terms = self.parse_equation(working[var], var)
            if self.debug:
                print(f"Coefficient récursif: '{coeff}'")
                print(f"Autres termes: {other_terms}")
            solution = self.apply_arden_lemma(coeff, other_terms)
            solution = self.simplify_expression(solution)
            if self.debug:
                print(f"Lemme d'Arden: {var} = {coeff}{var} + {other_terms}")
                print(f"                => {var} = {solution}")
            solutions[var] = solution
            working[var] = solution

            if self.debug:
                print(f"\nSubstitution de {var} = {solution} dans les autres équations:")
            for other_var in working:
                if other_var != var and self._contains_variable(working[other_var], var):
                    old = working[other_var]
                    working[other_var] = self.substitute_variable(old, var, solution)
                    if self.debug:
                        print(f"  {other_var}: {old} → {working[other_var]}")

        # Résolution directe
        for var in equations:
            if var not in solutions:
                if self.debug:
                    print(f"\n=== ÉTAPE {step}: Résolution directe de {var} ===")
                    step += 1
                    print(f"Équation: {var} = {working[var]}")
                coeff, other_terms = self.parse_equation(working[var], var)
                if coeff:
                    solution = self.apply_arden_lemma(coeff, other_terms)
                    method = "Lemme d'Arden (après substitution)"
                else:
                    solution = working[var] or "ε"
                    method = "Solution directe"
                solution = self.simplify_expression(solution)
                solutions[var] = solution
                if self.debug:
                    print(f"Méthode: {method}")
                    print(f"Solution: {var} = {solution}")

        # Substitution récursive jusqu'à stabilisation
        if self.debug:
            print("\n=== SUBSTITUTION FINALE ===")
        stabilisé = False
        while not stabilisé:
            stabilisé = True
            for var in solutions:
                expr = solutions[var]
                for other_var, other_expr in solutions.items():
                    if var != other_var and self._contains_variable(expr, other_var):
                        new_expr = self.substitute_variable(expr, other_var, other_expr)
                        new_expr = self.simplify_expression(new_expr)
                        if new_expr != expr:
                            if self.debug:
                                print(f"  {var}: {expr} → {new_expr}")
                            solutions[var] = new_expr
                            expr = new_expr
                            stabilisé = False

        if self.debug:
            print(f"\n=== SOLUTIONS FINALES ===")
            for var in equations:
                print(f"{var} = {solutions[var]}")
        return solutions

    def set_debug(self, debug: bool):
        self.debug = debug


def solve_automaton_system(equations: Dict[str, str], debug: bool = True) -> Dict[str, str]:
    solver = StrategicAutomatonSolver()
    solver.set_debug(debug)
    return solver.solve_system(equations)


if __name__ == "__main__":
    print("=" * 80)
    print("RÉSOLUTION SELON LA MÉTHODE DU LEMME D'ARDEN - VERSION CORRIGÉE")
    print("=" * 80)

    system = {
        'X1': 'bX1 + aX2',
        'X2': 'bX1 + aX2 + bX3 + ε',
        'X3': 'bX1'
    }

    solutions = solve_automaton_system(system)

    print("\n" + "=" * 50)
    print("RÉSULTATS ATTENDUS vs OBTENUS:")
    print("=" * 50)
    print("ATTENDUS:")
    print("X1 = b*a(bb*a + a + bbb*a)*")
    print("X2 = (bb*a + a + bbb*a)*")
    print("X3 = bb*a(bb*a + a + bbb*a)*")
    print("\nOBTENUS:")
    for var, sol in solutions.items():
        print(f"{var} = {sol}")

