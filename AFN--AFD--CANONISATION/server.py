from flask import Flask, request, jsonify
from flask import render_template
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Automate:
    def __init__(self, alphabet, etats, transitions, initial, final):
        if not isinstance(alphabet, list) or not all(isinstance(s, str) for s in alphabet):
            raise ValueError("L'alphabet doit être une liste de chaînes.")
        if not isinstance(etats, list) or not all(isinstance(e, str) for e in etats):
            raise ValueError("Les états doivent être une liste de chaînes.")
        if not isinstance(transitions, dict):
            raise ValueError("Les transitions doivent être un dictionnaire.")
        if not isinstance(initial, str):
            raise ValueError("L'état initial doit être une chaîne.")
        if not isinstance(final, list) or not all(isinstance(f, str) for f in final):
            raise ValueError("Les états finaux doivent être une liste de chaînes.")

        self.alphabet = alphabet
        self.etats = etats
        self.transitions = transitions
        self.etat_initial = initial
        self.etats_final = final
        self.type = 'AFN'

    def to_dict(self):
        return {
            'alphabet': self.alphabet,
            'etats': self.etats,
            'transitions': self.transitions,
            'etat_initial': self.etat_initial,
            'etats_final': self.etats_final,
            'type': self.type
        }

    def is_deterministic(self):
        for etat in self.transitions:
            for symbole in self.transitions[etat]:
                destinations = self.transitions[etat][symbole]
                if isinstance(destinations, list) and len(destinations) > 1:
                    return False
                if not isinstance(destinations, (str, list)):
                    return False
        return True

    def convertir_afn_en_afd(self):
        nouveaux_etats = []
        nouvelles_transitions = {}
        nouveaux_finaux = []
        queue = []
        traites = set()

        etat_initial_afd = frozenset([self.etat_initial])
        queue.append(etat_initial_afd)
        nouveaux_etats.append(etat_initial_afd)

        while queue:
            etat_courant = queue.pop(0)
            if etat_courant in traites:
                continue
            traites.add(etat_courant)

            for symbole in self.alphabet:
                nouvel_etat = set()
                for etat in etat_courant:
                    if etat in self.transitions and symbole in self.transitions[etat]:
                        destinations = self.transitions[etat][symbole]
                        if isinstance(destinations, list):
                            nouvel_etat.update(destinations)
                        else:
                            nouvel_etat.add(destinations)

                if nouvel_etat:
                    nouvel_etat_frozen = frozenset(nouvel_etat)
                    if etat_courant not in nouvelles_transitions:
                        nouvelles_transitions[etat_courant] = {}
                    nouvelles_transitions[etat_courant][symbole] = nouvel_etat_frozen

                    if nouvel_etat_frozen not in nouveaux_etats:
                        nouveaux_etats.append(nouvel_etat_frozen)
                        queue.append(nouvel_etat_frozen)

        for etat in nouveaux_etats:
            if any(e in self.etats_final for e in etat):
                nouveaux_finaux.append(etat)

        etats_str = ['{' + ','.join(sorted(str(e) for e in etat)) + '}' for etat in nouveaux_etats]
        transitions_str = {}
        for etat, trans in nouvelles_transitions.items():
            etat_str = '{' + ','.join(sorted(str(e) for e in etat)) + '}'
            transitions_str[etat_str] = {}
            for symbole, dest in trans.items():
                dest_str = '{' + ','.join(sorted(str(e) for e in dest)) + '}'
                transitions_str[etat_str][symbole] = dest_str

        initial_str = '{' + ','.join(sorted(str(e) for e in etat_initial_afd)) + '}'
        finaux_str = ['{' + ','.join(sorted(str(e) for e in etat)) + '}' for etat in nouveaux_finaux]

        afd = Automate(self.alphabet, etats_str, transitions_str, initial_str, finaux_str)
        afd.type = 'AFD'
        return afd

    def tester_mot_afd(self, mot):
        etat_courant = self.etat_initial
        chemin = [etat_courant]

        for symbole in mot:
            if etat_courant in self.transitions and symbole in self.transitions[etat_courant]:
                etat_courant = self.transitions[etat_courant][symbole]
                chemin.append(etat_courant)
            else:
                return False, chemin

        return etat_courant in self.etats_final, chemin

    def tester_mot_afn(self, mot):
        def explorer(etat, index_mot, chemin):
            if index_mot == len(mot):
                return etat in self.etats_final, chemin

            symbole = mot[index_mot]
            if etat in self.transitions and symbole in self.transitions[etat]:
                destinations = self.transitions[etat][symbole]
                if isinstance(destinations, list):
                    for dest in destinations:
                        resultat, nouveau_chemin = explorer(dest, index_mot + 1, chemin + [dest])
                        if resultat:
                            return True, nouveau_chemin
                else:
                    return explorer(destinations, index_mot + 1, chemin + [destinations])

            return False, chemin

        return explorer(self.etat_initial, 0, [self.etat_initial])

    def tester_mot(self, mot):
        if not isinstance(mot, str):
            raise ValueError("Le mot doit être une chaîne.")
        if self.type == 'AFD':
            return self.tester_mot_afd(mot)
        else:
            return self.tester_mot_afn(mot)

    def canoniser(self):
        mapping = {}
        etats_tries = sorted(self.etats)

        mapping[self.etat_initial] = 'q0'
        compteur = 1
        for etat in etats_tries:
            if etat != self.etat_initial:
                mapping[etat] = 'q' + str(compteur)
                compteur += 1

        nouveaux_etats = sorted(mapping.values())
        nouvelles_transitions = {}
        for ancien_etat, nouveau_etat in mapping.items():
            if ancien_etat in self.transitions:
                nouvelles_transitions[nouveau_etat] = {}
                for symbole, destinations in self.transitions[ancien_etat].items():
                    if isinstance(destinations, list):
                        nouvelles_transitions[nouveau_etat][symbole] = sorted([mapping[dest] for dest in destinations])
                    else:
                        nouvelles_transitions[nouveau_etat][symbole] = mapping[destinations]

        nouveaux_finaux = sorted([mapping[etat] for etat in self.etats_final])
        automate_canonique = Automate(
            sorted(self.alphabet),
            nouveaux_etats,
            nouvelles_transitions,
            mapping[self.etat_initial],
            nouveaux_finaux
        )
        automate_canonique.type = self.type
        return automate_canonique

@app.route('/api/automate', methods=['POST'])
def create_automate():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Aucune donnée fournie.")

        alphabet = data.get('alphabet', [])
        etats = data.get('etats', [])
        transitions = data.get('transitions', {})
        initial = data.get('etat_initial', '')
        final = data.get('etats_final', [])

        if not all(isinstance(x, list) for x in (alphabet, etats, final)):
            raise ValueError("Alphabet, états et états finaux doivent être des listes.")
        if not isinstance(transitions, dict):
            raise ValueError("Transitions doivent être un dictionnaire.")
        if not isinstance(initial, str):
            raise ValueError("État initial doit être une chaîne.")

        automate = Automate(alphabet, etats, transitions, initial, final)
        automate.type = 'AFD' if automate.is_deterministic() else 'AFN'

        logger.info(f"Automate créé : type={automate.type}")
        return jsonify({
            'success': True,
            'automate': automate.to_dict(),
            'message': f'Automate créé avec succès (Type: {automate.type})'
        })

    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500

@app.route('/api/convert', methods=['POST'])
def convert_afn_to_afd():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Aucune donnée fournie.")

        automate = Automate(
            data.get('alphabet', []),
            data.get('etats', []),
            data.get('transitions', {}),
            data.get('etat_initial', ''),
            data.get('etats_final', [])
        )

        if automate.is_deterministic():
            raise ValueError("L'automate est déjà déterministe.")

        afd = automate.convertir_afn_en_afd()
        logger.info("Conversion AFN → AFD réussie")
        return jsonify({
            'success': True,
            'afd': afd.to_dict(),
            'message': 'Conversion AFN → AFD réussie'
        })

    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500

@app.route('/api/test', methods=['POST'])
def test_word():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Aucune donnée fournie.")

        mot = data.get('mot', '')
        if not isinstance(mot, str):
            raise ValueError("Le mot doit être une chaîne.")

        automate = Automate(
            data.get('alphabet', []),
            data.get('etats', []),
            data.get('transitions', {}),
            data.get('etat_initial', ''),
            data.get('etats_final', [])
        )
        automate.type = data.get('type', 'AFN')

        accepte, chemin = automate.tester_mot(mot)
        logger.info(f"Test du mot '{mot}' : {'accepté' if accepte else 'rejeté'}")
        return jsonify({
            'success': True,
            'accepte': accepte,
            'chemin': chemin,
            'mot': mot,
            'message': f'Mot "{mot}" {"accepté" if accepte else "rejeté"}'
        })

    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    try:
        examples = {
            'simple': {
                'alphabet': ['a', 'b'],
                'etats': ['q0', 'q1', 'q2'],
                'transitions': {
                    'q0': {'a': ['q1'], 'b': ['q0']},
                    'q1': {'a': ['q2'], 'b': ['q1']},
                    'q2': {'a': ['q2'], 'b': ['q2']}
                },
                'etat_initial': 'q0',
                'etats_final': ['q2'],
                'description': 'AFN acceptant les mots contenant au moins deux "a"'
            },
            'complex': {
                'alphabet': ['a', 'b'],
                'etats': ['1', '2', '3', '4'],
                'transitions': {
                    '1': {'a': ['1', '2']},
                    '2': {'a': ['4'], 'b': ['3']},
                    '3': {'b': ['3', '4']}
                },
                'etat_initial': '1',
                'etats_final': ['4'],
                'description': 'AFN avec transitions non-déterministes'
            },
            'binary': {
                'alphabet': ['0', '1'],
                'etats': ['q0', 'q1', 'q2'],
                'transitions': {
                    'q0': {'0': ['q0'], '1': ['q0', 'q1']},
                    'q1': {'0': ['q2'], '1': ['q2']},
                    'q2': {}
                },
                'etat_initial': 'q0',
                'etats_final': ['q2'],
                'description': 'AFN acceptant les nombres binaires se terminant par 10 ou 11'
            }
        }

        logger.info("Exemples d'automates récupérés")
        return jsonify({
            'success': True,
            'examples': examples
        })

    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_automate():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Aucune donnée fournie.")

        errors = []
        warnings = []

        if not data.get('alphabet'):
            errors.append("L'alphabet ne peut pas être vide")
        if not data.get('etats'):
            errors.append("La liste des états ne peut pas être vide")
        if not data.get('etat_initial'):
            errors.append("L'état initial doit être spécifié")
        if not data.get('etats_final'):
            warnings.append("Aucun état final spécifié")

        if data.get('etat_initial') and data.get('etat_initial') not in data.get('etats', []):
            errors.append("L'état initial doit être dans la liste des états")

        for etat in data.get('etats_final', []):
            if etat not in data.get('etats', []):
                errors.append(f"L'état final '{etat}' n'existe pas dans la liste des états")

        transitions = data.get('transitions', {})
        for etat, trans in transitions.items():
            if etat not in data.get('etats', []):
                errors.append(f"L'état '{etat}' dans les transitions n'existe pas")
            for symbole, destinations in trans.items():
                if symbole not in data.get('alphabet', []):
                    errors.append(f"Le symbole '{symbole}' n'est pas dans l'alphabet")
                if isinstance(destinations, list):
                    for dest in destinations:
                        if dest not in data.get('etats', []):
                            errors.append(f"L'état destination '{dest}' n'existe pas")
                else:
                    if destinations not in data.get('etats', []):
                        errors.append(f"L'état destination '{destinations}' n'existe pas")

        logger.info("Validation effectuée : valide si pas d'erreurs sinon invalide")
        return jsonify({
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        })

    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500

@app.route('/api/canonize', methods=['POST'])
def canonize_automate():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Aucune donnée fournie.")

        automate = Automate(
            data.get('alphabet', []),
            data.get('etats', []),
            data.get('transitions', {}),
            data.get('etat_initial', ''),
            data.get('etats_final', [])
        )

        automate_canonique = automate.canoniser()
        logger.info("Canonisation réussie")
        return jsonify({
            'success': True,
            'automate': automate_canonique.to_dict(),
            'message': 'Canonisation réussie'
        })

    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return jsonify({
            'success': False,
            'error': "Erreur serveur interne"
        }), 500
    
@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5004)
