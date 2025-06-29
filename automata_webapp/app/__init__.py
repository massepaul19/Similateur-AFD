from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from app.models.automate import db


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:massepaul17@localhost/automates_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Enregistrement des blueprints
    from app.views.main import main_bp
    from app.views.conversions import conversions_bp
    from app.views.operations import operations_bp
    from app.views.visualizations import visualizations_bp
    from app.views.expressions import expressions_bp
    from app.views.automate import  automate_bp
    from app.views.nfa_to_dfa import nfa_to_dfa_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(nfa_to_dfa_bp, url_prefix='/nfa_to_dfa')
    app.register_blueprint(conversions_bp, url_prefix='/conversions')
    app.register_blueprint(automate_bp, url_prefix='/api')
    app.register_blueprint(operations_bp, url_prefix='/operations')
    app.register_blueprint(visualizations_bp, url_prefix='/visualizations')
    app.register_blueprint(expressions_bp, url_prefix='/expressions')

    with app.app_context():
        db.create_all()  # Crée les tables si elles n'existent pas
    
    return app

