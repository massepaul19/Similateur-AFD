from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.services.automaton_service import AutomatonService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload_automaton():
    """Upload d'un automate"""
    if request.method == 'POST':
        # TODO: Gérer l'upload de fichier
        pass
    return render_template('upload.html')

@main_bp.route('/automate/nouveau', methods=['GET'])
def create_automaton():
    """Page de création d'un automate"""
    return render_template('create_automate.html')


@main_bp.route('/automate', methods=['GET'])
def my_automata():
    """Page listant tous les automates enregistrés"""
    # Tu peux plus tard charger les automates depuis une base ou un fichier
    return render_template('mes_automates.html')
@main_bp.route('/systems' , methods=['GET']) 
def resoudre_systeme():
    return render_template('operations/solve_system.html')