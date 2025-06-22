# automate_operations.py

def est_deterministe(transitions):
    """Vérifie si l'automate est un DFA"""
    for etat in transitions:
        for symbole in transitions[etat]:
            destinations = transitions[etat][symbole]
            if len(destinations) != 1:
                return False
    return True


def convertir_afn_en_afd(transitions, alphabet, etat_initial, etats_finaux):
    """Convertit un AFN en AFD"""
    if est_deterministe(transitions):
        return None, "Cet automate est déjà déterministe."

    nouvelle_transition = {}
    nouveaux_etats = []
    nouvelle_etiquette = {}
    file_attente = []

    # État initial de l’AFD = ensemble contenant l’état initial de l’AFN
    initial = frozenset([etat_initial])
    file_attente.append(initial)
    nouvelle_etiquette[initial] = nom_etat(initial)
    nouvelle_transition[nouvelle_etiquette[initial]] = {}
    nouveaux_etats.append(nouvelle_etiquette[initial])

    nouveaux_etats_finaux = set()

    while file_attente:
        courant = file_attente.pop(0)
        nom_courant = nouvelle_etiquette[courant]

        nouvelle_transition[nom_courant] = {}

        for symbole in alphabet:
            destination = set()
            for etat in courant:
                if symbole in transitions[etat]:
                    destination.update(transitions[etat][symbole])
            if not destination:
                continue

            dest_frozen = frozenset(destination)
            if dest_frozen not in nouvelle_etiquette:
                nom_dest = nom_etat(dest_frozen)
                nouvelle_etiquette[dest_frozen] = nom_dest
                file_attente.append(dest_frozen)
                nouveaux_etats.append(nom_dest)

            nouvelle_transition[nom_courant][symbole] = [nouvelle_etiquette[dest_frozen]]

    # États finaux de l’AFD : tout ensemble contenant au moins un état final de l’AFN
    for etat_set, nom in nouvelle_etiquette.items():
        if any(e in etats_finaux for e in etat_set):
            nouveaux_etats_finaux.add(nom)

    return {
        "alphabet": alphabet,
        "etats": nouveaux_etats,
        "etat_initial": nouvelle_etiquette[initial],
        "etats_finaux": list(nouveaux_etats_finaux),
        "transitions": nouvelle_transition
    }, None


def nom_etat(ensemble_etats):
    """Donne un nom lisible à un ensemble d'états"""
    return "{" + ",".join(sorted(ensemble_etats)) + "}"


#epsilon

def epsilon_closure(transitions, etat):
    """Retourne la fermeture epsilon (ensemble d'états accessibles via ε)"""
    stack = [etat]
    closure = {etat}
    while stack:
        courant = stack.pop()
        for suivant in transitions.get(courant, {}).get('ε', []):
            if suivant not in closure:
                closure.add(suivant)
                stack.append(suivant)
    return closure


def epsilon_afn_to_afd(transitions, alphabet, etat_initial, etats_finaux):
    """Convertit un epsilon-AFN en AFD"""
    alphabet = [a for a in alphabet if a != 'ε']  # On enlève epsilon du vrai alphabet

    # Fermeture epsilon de l’état initial
    initial_closure = frozenset(epsilon_closure(transitions, etat_initial))
    file_attente = [initial_closure]
    etiquettes = {initial_closure: nom_etat(initial_closure)}
    nouveau_transitions = {}
    nouveaux_etats = []
    nouveaux_etats_finaux = set()

    while file_attente:
        courant = file_attente.pop(0)
        nom_courant = etiquettes[courant]
        nouveaux_etats.append(nom_courant)
        nouveau_transitions[nom_courant] = {}

        for symbole in alphabet:
            destination = set()
            for etat in courant:
                suivants = transitions.get(etat, {}).get(symbole, [])
                for suivant in suivants:
                    destination.update(epsilon_closure(transitions, suivant))

            if not destination:
                continue

            frozen_dest = frozenset(destination)
            if frozen_dest not in etiquettes:
                etiquettes[frozen_dest] = nom_etat(frozen_dest)
                file_attente.append(frozen_dest)

            nouveau_transitions[nom_courant][symbole] = [etiquettes[frozen_dest]]

    # Déterminer les nouveaux états finaux
    for etat_set, nom in etiquettes.items():
        if any(e in etats_finaux for e in etat_set):
            nouveaux_etats_finaux.add(nom)

    return {
        "alphabet": alphabet,
        "etats": list(etiquettes.values()),
        "etat_initial": etiquettes[initial_closure],
        "etats_finaux": list(nouveaux_etats_finaux),
        "transitions": nouveau_transitions,
    }

#automate complet
def completer_afd(transitions, alphabet):
    if not est_deterministe(transitions):
        return None, "Cet automate n'est pas déterministe. Impossible de le compléter."

    etats = list(transitions.keys())
    etat_puits = "⊥"
    complet = True

    # Créer une copie profonde des transitions
    new_transitions = {e: dict(transitions[e]) for e in transitions}

    # Détection de transitions manquantes et ajout du puits si besoin
    for etat in etats:
        if etat not in new_transitions:
            new_transitions[etat] = {}
        for symb in alphabet:
            if symb not in new_transitions[etat]:
                complet = False
                if etat_puits not in new_transitions:
                    new_transitions[etat_puits] = {}
                new_transitions[etat][symb] = [etat_puits]

    # Si on a dû ajouter le puits, on complète ses propres transitions
    if etat_puits in new_transitions:
        for symb in alphabet:
            new_transitions[etat_puits][symb] = [etat_puits]

    return new_transitions, etat_puits if not complet else None

#emondage automate

def emonder_automate(transitions, etat_initial, etats_finaux):
    # Étape 1 : états accessibles depuis l’état initial
    def accessibles():
        vus = set()
        stack = [etat_initial]
        while stack:
            etat = stack.pop()
            if etat not in vus:
                vus.add(etat)
                for symbole in transitions.get(etat, {}):
                    for succ in transitions[etat][symbole]:
                        stack.append(succ)
        return vus

    # Étape 2 : états coaccessibles (ceux qui mènent à un état final)
    def coaccessibles():
        inverse = {}
        for e in transitions:
            for s in transitions[e]:
                for dest in transitions[e][s]:
                    inverse.setdefault(dest, []).append(e)

        vus = set()
        stack = list(etats_finaux)
        while stack:
            etat = stack.pop()
            if etat not in vus:
                vus.add(etat)
                for pred in inverse.get(etat, []):
                    stack.append(pred)
        return vus

    acces = accessibles()
    coacces = coaccessibles()
    utiles = acces & coacces  # intersection

    # On garde uniquement les états utiles
    emonde_transitions = {}
    for e in transitions:
        if e in utiles:
            emonde_transitions[e] = {}
            for s in transitions[e]:
                # On garde uniquement les transitions qui vont aussi vers des états utiles
                dests = [d for d in transitions[e][s] if d in utiles]
                if dests:
                    emonde_transitions[e][s] = dests

    emonde_etats_finaux = [e for e in etats_finaux if e in utiles]

    return {
        "transitions": emonde_transitions,
        "etats": list(utiles),
        "etat_initial": etat_initial if etat_initial in utiles else None,
        "etats_finaux": emonde_etats_finaux
    }

#minimisation

def minimiser_afd(transitions, alphabet, etat_initial, etats_finaux):
    from collections import defaultdict

    # Étape 1 : compléter
    transitions_complets, _ = completer_afd(transitions, alphabet)
    if transitions_complets is None:
        return None, "L'automate n'est pas déterministe. Impossible de minimiser."

    # Étape 2 : initialiser les partitions
    F = set(etats_finaux)
    Q = set(transitions_complets.keys())
    non_F = Q - F
    partitions = [F, non_F]

    def trouver_classe(partitions, etat):
        for i, part in enumerate(partitions):
            if etat in part:
                return i
        return -1

    # Étape 3 : affiner les partitions
    while True:
        nouvelles_partitions = []
        for groupe in partitions:
            sous_groupes = defaultdict(set)
            for e in groupe:
                signature = tuple(trouver_classe(partitions, transitions_complets[e][a][0]) for a in alphabet)
                sous_groupes[signature].add(e)
            nouvelles_partitions.extend(sous_groupes.values())
        if nouvelles_partitions == partitions:
            break
        partitions = nouvelles_partitions

    # Étape 4 : construire l'automate minimal
    etat_map = {}
    for i, groupe in enumerate(partitions):
        for etat in groupe:
            etat_map[etat] = f"P{i}"

    nouveaux_etats = list(set(etat_map.values()))
    nouvel_etat_initial = etat_map[etat_initial]
    nouveaux_etats_finaux = list({etat_map[e] for e in F})
    nouvelles_transitions = {}

    for groupe in partitions:
        representant = next(iter(groupe))
        e_nom = etat_map[representant]
        nouvelles_transitions[e_nom] = {}
        for a in alphabet:
            cible = transitions_complets[representant][a][0]
            nouvelles_transitions[e_nom][a] = [etat_map[cible]]

    return {
        "etats": nouveaux_etats,
        "etat_initial": nouvel_etat_initial,
        "etats_finaux": nouveaux_etats_finaux,
        "transitions": nouvelles_transitions
    }, ""

def afn_to_epsilon_afn(transitions):
    """
    Convertit un AFN en ε-AFN en ajoutant des ε-transitions vides (structure inchangée).
    """
    epsilon_afn = {}

    for e in transitions:
        epsilon_afn[e] = {}
        for a in transitions[e]:
            epsilon_afn[e][a] = transitions[e][a]
        # On ajoute la clé epsilon même si vide
        epsilon_afn[e]["ε"] = []

    return epsilon_afn


def epsilon_afn_to_afn(transitions):
    """
    Convertit un ε-AFN en AFN en supprimant les ε-transitions
    (en calculant les ε-fermetures de chaque état).
    """
    # Étape 1 : calculer les ε-fermetures
    def epsilon_fermeture(etat):
        pile = [etat]
        ferme = set([etat])
        while pile:
            courant = pile.pop()
            for voisin in transitions.get(courant, {}).get("ε", []):
                if voisin not in ferme:
                    ferme.add(voisin)
                    pile.append(voisin)
        return ferme

    nouveaux_trans = {}
    for e in transitions:
        fermeture_e = epsilon_fermeture(e)
        nouveaux_trans[e] = {}

        for symbole in transitions[e]:
            if symbole == "ε":
                continue
            destinations = set()
            for f in fermeture_e:
                destinations.update(transitions.get(f, {}).get(symbole, []))
                # inclure la fermeture de ces états aussi
            new_dest = set()
            for d in destinations:
                new_dest.update(epsilon_fermeture(d))
            if symbole not in nouveaux_trans[e]:
                nouveaux_trans[e][symbole] = []
            nouveaux_trans[e][symbole].extend(sorted(new_dest))

    return nouveaux_trans
