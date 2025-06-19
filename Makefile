#Lancer automatiquement les serveurs

# Lancer un projet individuel

afd-afn:
	cd AFD-AFN && python3 app.py

system:
	cd Systemes_equations && python3 app.py

# Lancer tous les projets en même temps (en arrière-plan)

run-all:
	cd "AFD-AFN" && python3 app.py &
	cd "Systemes_equations" && python3 app.py &
	@echo "Tous les serveurs sont lancés en arrière-plan"
	@echo "Utilisez 'make stop' pour les arrêter"

# Arrêter tous les serveurs Python

stop:
	pkill -f "python3 app.py" || true

# Voir les serveurs qui tournent

status:
	@echo "Serveurs Python en cours d'exécution:"
	@ps aux | grep "python3 app.py" | grep -v grep || echo "Aucun serveur détecté"

#j'efface le terminal

clean:
	clear
	
# Aide

help:
	@echo "Commandes disponibles:"
	@echo "  make afd-afn    - Lancer AFD-AFN (port 5002)"
	@echo "  make system     - Lancer Systemes_equations (port 5001)"
	@echo "  make projet3    - Lancer Projet3"
	@echo "  make run-all    - Lancer tous les projets"
	@echo "  make stop       - Arrêter tous les serveurs"
	@echo "  make status     - Voir les serveurs actifs"
	@echo "  make clean      - Effacer le terminal"
	
