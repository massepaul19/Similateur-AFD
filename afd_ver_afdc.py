def completer_afd(automate):
    """
    Complète un AFD en ajoutant un état puits pour les transitions manquantes.
    Version robuste avec vérification des entrées et gestion des erreurs.
    
    Args:
        automate (dict): Dictionnaire contenant:
            - 'Etats' (list): Liste des états (str)
            - 'Etat_initial' (str): Nom de l'état initial
            - 'Etats_finaux' (list): Liste des états finaux
            - 'transitions' (list): Liste de transitions [état_départ, symbole, état_arrivée]
            - 'alphabet' (list): Liste des symboles de l'alphabet
    
    Returns:
        dict: L'automate complété avec les mêmes clés
    """
    # Vérification de la structure de l'automate
    required_keys = ['Etats', 'Etat_initial', 'Etats_finaux', 'transitions', 'alphabet']
    if not all(key in automate for key in required_keys):
        raise ValueError("Structure d'automate invalide. Clés requises: " + ", ".join(required_keys))
    
    # Vérification des types
    if not isinstance(automate['Etats'], list) or not all(isinstance(e, str) for e in automate['Etats']):
        raise ValueError("'Etats' doit être une liste de strings")
    
    if not isinstance(automate['Etat_initial'], str):
        raise ValueError("'Etat_initial' doit être une string")
    
    if not isinstance(automate['Etats_finaux'], list) or not all(isinstance(e, str) for e in automate['Etats_finaux']):
        raise ValueError("'Etats_finaux' doit être une liste de strings")
    
    # Vérification que l'état initial existe
    if automate['Etat_initial'] not in automate['Etats']:
        raise ValueError(f"L'état initial '{automate['Etat_initial']}' n'existe pas dans la liste des états")
    
    # Copie profonde des données
    etats = automate['Etats'].copy()
    etat_initial = automate['Etat_initial']
    etats_finaux = automate['Etats_finaux'].copy()
    alphabet = automate['alphabet'].copy()
    transitions = [t.copy() for t in automate['transitions']]
    
    # Construction de la table des transitions
    table_transitions = {}
    for depart, symbole, arrivee in transitions:
        if (depart, symbole) in table_transitions:
            raise ValueError(f"Transition non déterministe: {depart} --{symbole}--> {arrivee} (existe déjà)")
        table_transitions[(depart, symbole)] = arrivee
    
    # Ajout des transitions manquantes
    etat_puits = "puits"
    transitions_a_ajouter = []
    besoin_puits = False
    
    for etat in etats:
        for symbole in alphabet:
            if (etat, symbole) not in table_transitions:
                transitions_a_ajouter.append([etat, symbole, etat_puits])
                besoin_puits = True
    
    # Ajout de l'état puits si nécessaire
    if besoin_puits:
        if etat_puits not in etats:
            etats.append(etat_puits)
        for symbole in alphabet:
            transitions_a_ajouter.append([etat_puits, symbole, etat_puits])
    
    return {
        'Etats': etats,
        'Etat_initial': etat_initial,
        'Etats_finaux': etats_finaux,
        'transitions': transitions + transitions_a_ajouter,
        'alphabet': alphabet
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # AFD incomplet (manque certaines transitions)
    afd_incomplet = {
        'Etats': ['q0', 'q1'],
        'Etat_initial': 'q0',
        'Etats_finaux': ['q1'],
        'transitions': [
            ['q0', 'a', 'q1'],
            ['q1', 'b', 'q1']
        ],
        'alphabet': ['a', 'b']
    }
    
    print("AFD incomplet:")
    print(afd_incomplet)
    
    try:
        afdc = completer_afd(afd_incomplet)
        print("\nAFD complété (AFDC):")
        print(afdc)
    except ValueError as e:
        print(f"\nErreur: {e}")