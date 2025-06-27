# models.py - Modèles SQLAlchemy pour les automates

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Automate(db.Model):
    __tablename__ = 'automates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # 'afd', 'afn', 'epsilon-afn', 'afdc'
    alphabet = db.Column(db.JSON, nullable=False)  # Liste des symboles
    initial_state = db.Column(db.String(50))
    config = db.Column(db.JSON)  # Configuration spécifique au type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    states = db.relationship('AutomateState', backref='automate', cascade='all, delete-orphan')
    transitions = db.relationship('AutomateTransition', backref='automate', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Automate {self.name} ({self.type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'alphabet': self.alphabet,
            'initial_state': self.initial_state,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'states': [state.to_dict() for state in self.states],
            'transitions': [transition.to_dict() for transition in self.transitions]
        }

class AutomateState(db.Model):
    __tablename__ = 'automate_states'
    
    id = db.Column(db.Integer, primary_key=True)
    automate_id = db.Column(db.Integer, db.ForeignKey('automates.id'), nullable=False)
    state_id = db.Column(db.String(50), nullable=False)  # 'q0', 'q1', etc.
    x = db.Column(db.Float, nullable=False)  # Position X sur le canvas
    y = db.Column(db.Float, nullable=False)  # Position Y sur le canvas
    is_initial = db.Column(db.Boolean, default=False)
    is_final = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AutomateState {self.state_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'state_id': self.state_id,
            'x': self.x,
            'y': self.y,
            'is_initial': self.is_initial,
            'is_final': self.is_final
        }

class AutomateTransition(db.Model):
    __tablename__ = 'automate_transitions'
    
    id = db.Column(db.Integer, primary_key=True)
    automate_id = db.Column(db.Integer, db.ForeignKey('automates.id'), nullable=False)
    from_state = db.Column(db.String(50), nullable=False)
    to_state = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # Symbole de transition
    
    def __repr__(self):
        return f'<AutomateTransition {self.from_state} --{self.symbol}--> {self.to_state}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_state': self.from_state,
            'to_state': self.to_state,
            'symbol': self.symbol
        }

# Service pour la logique métier
class AutomateService:
    
    @staticmethod
    def create_automate(data):
        """Créer un nouvel automate avec ses états et transitions"""
        try:
            # Créer l'automate principal
            automate = Automate(
                name=data['name'],
                description=data.get('description', ''),
                type=data['type'],
                alphabet=data['alphabet'],
                initial_state=data.get('initialState'),
                config=data.get('config', {})
            )
            
            db.session.add(automate)
            db.session.flush()  # Pour obtenir l'ID
            
            # Créer les états
            for state_data in data.get('states', []):
                state = AutomateState(
                    automate_id=automate.id,
                    state_id=state_data['id'],
                    x=state_data['x'],
                    y=state_data['y'],
                    is_initial=state_data.get('isInitial', False),
                    is_final=state_data.get('isFinal', False)
                )
                db.session.add(state)
            
            # Créer les transitions
            for transition_key, destinations in data.get('transitions', []):
                from_state, symbol = transition_key.split(',')
                for to_state in destinations:
                    transition = AutomateTransition(
                        automate_id=automate.id,
                        from_state=from_state,
                        to_state=to_state,
                        symbol=symbol
                    )
                    db.session.add(transition)
            
            db.session.commit()
            return automate
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_automate(automate_id):
        """Récupérer un automate par son ID"""
        return Automate.query.get_or_404(automate_id)
    
    @staticmethod
    def update_automate(automate_id, data):
        """Mettre à jour un automate existant"""
        try:
            automate = Automate.query.get_or_404(automate_id)
            
            # Mettre à jour les propriétés de base
            automate.name = data.get('name', automate.name)
            automate.description = data.get('description', automate.description)
            automate.type = data.get('type', automate.type)
            automate.alphabet = data.get('alphabet', automate.alphabet)
            automate.initial_state = data.get('initialState', automate.initial_state)
            automate.config = data.get('config', automate.config)
            automate.updated_at = datetime.utcnow()
            
            # Supprimer les anciens états et transitions
            AutomateState.query.filter_by(automate_id=automate.id).delete()
            AutomateTransition.query.filter_by(automate_id=automate.id).delete()
            
            # Recréer les états et transitions
            for state_data in data.get('states', []):
                state = AutomateState(
                    automate_id=automate.id,
                    state_id=state_data['id'],
                    x=state_data['x'],
                    y=state_data['y'],
                    is_initial=state_data.get('isInitial', False),
                    is_final=state_data.get('isFinal', False)
                )
                db.session.add(state)
            
            for transition_key, destinations in data.get('transitions', []):
                from_state, symbol = transition_key.split(',')
                for to_state in destinations:
                    transition = AutomateTransition(
                        automate_id=automate.id,
                        from_state=from_state,
                        to_state=to_state,
                        symbol=symbol
                    )
                    db.session.add(transition)
            
            db.session.commit()
            return automate
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_automate(automate_id):
        """Supprimer un automate"""
        try:
            automate = Automate.query.get_or_404(automate_id)
            db.session.delete(automate)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def list_automates():
        """Lister tous les automates"""
        return Automate.query.order_by(Automate.created_at.desc()).all()
    
    @staticmethod
    def validate_automate_data(data):
        """Valider les données d'un automate"""
        errors = []
        
        # Vérifications de base
        if not data.get('name'):
            errors.append("Le nom de l'automate est requis")
        
        if not data.get('type') or data['type'] not in ['afd', 'afn', 'epsilon-afn', 'afdc']:
            errors.append("Type d'automate invalide")
        
        if not data.get('alphabet') or len(data['alphabet']) == 0:
            errors.append("L'alphabet ne peut pas être vide")
        
        if not data.get('states') or len(data['states']) == 0:
            errors.append("L'automate doit avoir au moins un état")
        
        # Vérifications spécifiques selon le type
        if data.get('type') == 'afdc':
            # Vérifier la complétude pour AFDC
            states = {s['id'] for s in data.get('states', [])}
            alphabet = set(data.get('alphabet', []))
            alphabet.discard('ε')  # Retirer epsilon pour AFDC
            
            transitions = {}
            for transition_key, destinations in data.get('transitions', []):
                transitions[transition_key] = destinations
            
            for state in states:
                for symbol in alphabet:
                    key = f"{state},{symbol}"
                    if key not in transitions:
                        errors.append(f"Transition manquante: {state} --{symbol}-->")
        
        return errors