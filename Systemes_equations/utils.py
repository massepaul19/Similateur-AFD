"""
Utilitaires pour la distribution des expressions régulières
"""
import re

######################################################################################## 

    #Cette fonction va me permettre de gerer A(B + ε) ou A(ε + B) = AB + A
    
   ##################
   
def distribute_concatenation(expression):
    """Distribue les concaténations avec des sommes contenant ε"""
    
    def find_matching_paren(text, start):
        """Trouve la parenthèse fermante correspondante"""
        count = 1
        i = start + 1
        while i < len(text) and count > 0:
            if text[i] == '(':
                count += 1
            elif text[i] == ')':
                count -= 1
            i += 1
        return i - 1 if count == 0 else -1
    
    def extract_terms_with_epsilon(content):
        """Extrait les termes d'une expression contenant + et ε"""
        terms = []
        current_term = ""
        paren_count = 0
        
        i = 0
        while i < len(content):
            char = content[i]
            if char == '(':
                paren_count += 1
                current_term += char
            elif char == ')':
                paren_count -= 1
                current_term += char
            elif char == '+' and paren_count == 0:
                terms.append(current_term.strip())
                current_term = ""
            else:
                current_term += char
            i += 1
        
        if current_term.strip():
            terms.append(current_term.strip())
        
        return terms
    
    result = expression
    changed = True
    
    # Boucle jusqu'à ce qu'aucun changement ne soit détecté
    while changed:
        changed = False
        i = 0
        
        while i < len(result):
            if result[i] == '(':
                # Trouver la parenthèse fermante
                close_paren = find_matching_paren(result, i)
                if close_paren == -1:
                    i += 1
                    continue
                
                # Extraire le contenu entre parenthèses
                content = result[i+1:close_paren]
                
                # Vérifier si le contenu contient + et ε
                if '+' in content and 'ε' in content:
                    # Trouver le préfixe
                    prefix_start = i - 1
                    while prefix_start >= 0 and result[prefix_start] not in ['+', ' '] or \
                          (prefix_start > 0 and result[prefix_start-1:prefix_start+1] in [')*', ')(']):
                        prefix_start -= 1
                    
                    if prefix_start >= 0 and result[prefix_start] in ['+', ' ']:
                        prefix_start += 1
                    elif prefix_start < 0:
                        prefix_start = 0
                    
                    prefix = result[prefix_start:i].strip()
                    
                    if prefix:  # S'il y a un préfixe à distribuer
                        # Extraire les termes
                        terms = extract_terms_with_epsilon(content)
                        
                        # Distribuer le préfixe
                        distributed_terms = []
                        for term in terms:
                            if term == 'ε':
                                distributed_terms.append(prefix)
                            else:
                                distributed_terms.append(f"{prefix}{term}")
                        
                        # Reconstruire l'expression
                        new_part = ' + '.join(distributed_terms)
                        result = result[:prefix_start] + new_part + result[close_paren+1:]
                        changed = True
                        break
                
                i = close_paren + 1
            else:
                i += 1
    
    return result


########################################################################################    
    
    # Cette partie permet simplifier une expression reguliere
     
    
def simplify_expression(expression):
    """Simplifie une expression régulière"""
    if not expression or expression == "":
        return "ε"
    
    # Nettoyer les espaces
    expression = re.sub(r'\s+', ' ', expression.strip())
    
    # Distribution avant simplification
    expression = distribute_concatenation(expression)
    
    # NOUVELLES RÈGLES pour simplifier les parenthèses redondantes
    
    # 1. Simplifier (a) -> a (parenthèses autour d'un seul symbole)
    expression = re.sub(r'\(([a-zA-Z])\)', r'\1', expression)
    
    # 2. Simplifier (a)* -> a* (parenthèses redondantes avec étoile)
    expression = re.sub(r'\(([a-zA-Z])\)\*', r'\1*', expression)
    
    # 3. Simplifier (a*) -> a* (parenthèses autour d'une expression déjà avec étoile)
    expression = re.sub(r'\(([a-zA-Z]\*)\)', r'\1', expression)
    
    # 4. Simplifier les concaténations: (a)(b) -> ab
    expression = re.sub(r'\(([a-zA-Z])\)\(([a-zA-Z])\)', r'\1\2', expression)
    
    # 5. Simplifier (a*)(b) -> a*b
    expression = re.sub(r'\(([a-zA-Z]\*)\)\(([a-zA-Z])\)', r'\1\2', expression)
    
    # 6. Simplifier (a)(b*) -> ab*
    expression = re.sub(r'\(([a-zA-Z])\)\(([a-zA-Z]\*)\)', r'\1\2', expression)
    
    # 7. Simplifier (a*)(b*) -> a*b*
    expression = re.sub(r'\(([a-zA-Z]\*)\)\(([a-zA-Z]\*)\)', r'\1\2', expression)
    
    # 8. Pour les expressions comme (a*b): si pas de + à l'intérieur, enlever parenthèses
    def remove_redundant_parens(match):
        content = match.group(1)
        # Si pas de + dans le contenu, les parenthèses sont redondantes
        if '+' not in content:
            return content
        return match.group(0)  # Garder tel quel
    
    expression = re.sub(r'\(([a-zA-Z\*]+)\)', remove_redundant_parens, expression)
    
    # Règles existantes...
    # Enlever les parenthèses vides et les termes vides
    expression = re.sub(r'\(\s*\)', '', expression)
    expression = re.sub(r'\s*\+\s*\+', ' + ', expression)
    expression = re.sub(r'^\s*\+\s*', '', expression)
    expression = re.sub(r'\s*\+\s*$', '', expression)
    
    # Simplifier les concaténations avec ε (ε est neutre)
    expression = re.sub(r'([a-zA-Z*\(\)]+)\s*ε', r'\1', expression)
    expression = re.sub(r'ε\s*([a-zA-Z*\(\)]+)', r'\1', expression)
    
    # Simplification de a + ε
    expression = re.sub(r'([a-zA-Z\(\)\*]+)\(ε\)', r'\1', expression)
    
    # Simplifier les expressions *ε -> *
    expression = re.sub(r'\*ε\b', '*', expression)
    
    # Nettoyer les + multiples
    while ' + + ' in expression:
        expression = expression.replace(' + + ', ' + ')
    
    # Nettoyer les parenthèses inutiles autour de ε
    expression = re.sub(r'\(ε\)', 'ε', expression)
    
    return expression.strip() if expression.strip() else "ε"

