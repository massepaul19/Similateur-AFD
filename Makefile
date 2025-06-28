#Lancer automatiquement les serveurs
# Lancer un projet individuel

###########################################################

# ----------------------------------------------------
# =============== Démrrage des serveurs ==============
# ----------------------------------------------------

auto:
	cd automata_webapp && python3 run.py
	
system:
	cd Systemes_equations && python3 app.py

auto_util:
	cd Automates_utils && python3 app.py

afn-afd-can:
	cd AFN--AFD--CANONISATION && python3 app.py

# ----------------------------------------------------

# Lancer tous les projets en même temps (en arrière-plan)

run-all:
	cd "automata_webapp" && python3 run.py &
	cd "Systemes_equations" && python3 app.py &
	cd "Automates_utils" && python3 app.py &
	cd "FN--AFD--CANONISATION" && python3 app.py &
	@echo "Tous les serveurs sont lancés en arrière-plan"
	@echo "Auto_principale: http://localhost:5000"
	@echo "Systemes_equations: http://localhost:5001"
	@echo "Automate_utils:  http://localhost:5003"


###########################################################
# Arrêter tous les serveurs Python et Streamlit
stop:
	pkill -f "python3 app.py" || true
##	pkill -f "streamlit run" || true

###########################################################

# Voir les serveurs qui tournent

status:
	@echo "Serveurs en cours d'exécution:"
	@ps aux | grep "python3 app.py" | grep -v grep || echo "Aucun serveur Python détecté"
#	@ps aux | grep "streamlit run" | grep -v grep || echo "Aucun serveur Streamlit détecté"

###########################################################

#j'efface le terminal

clean:
	clear

###########################################################

#installation des dependances 

install_dep:
	@echo "Installation des dépendances..."
	pip3 install -r requirements.txt
	@echo "Installation terminée!"
         
###########################################################

# Aide

help:
	@echo "Commandes disponibles:"
	@echo "  automata_webapp 	- Lancer L'application principaleFN-EP-AFD (port 5000)"
	@echo "  make system     	- Lancer Systemes_equations (port 5001)" 
	@echo "  make auto_util  	- Lancer Automates_utils (port 5003)" 
	@echo "  make run-all    	- Lancer tous les projets"
	@echo "  make stop       	- Arrêter tous les serveurs"
	@echo "  make status     	- Voir les serveurs actifs"
	@echo "  make clean     	- Effacer le terminal"
	@echo "  install_dep     	- Installer les dépendances"
