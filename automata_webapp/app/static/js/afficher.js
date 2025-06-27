// afficher.js - JavaScript amélioré pour la gestion des automates
let currentFilter = 'all';
let automateToDelete = null;
const automateCards = document.querySelectorAll('.automate-card');
const filterTabs = document.querySelectorAll('.filter-tab');
const emptyState = document.getElementById('emptyState');
const automatesGrid = document.getElementById('automatesGrid');
const deleteModal = document.getElementById('deleteModal');

// Configuration des URLs (à adapter selon votre routing Flask)
const API_URLS = {
    automates: '/api/automates',
    delete: (id) => `/api/automates/${id}`,
    visualize: (id) => `/automates/${id}/visualize`,
    edit: (id) => `/automates/${id}/edit`,
    export: (id) => `/automates/${id}/export`
};

// Filter functionality
function initializeFilters() {
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const filterType = this.dataset.type;
            setActiveFilter(filterType);
            filterAutomates(filterType);
        });
    });
}

function setActiveFilter(filterType) {
    currentFilter = filterType;
    filterTabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.type === filterType) {
            tab.classList.add('active');
        }
    });
}

function filterAutomates(filterType) {
    let visibleCount = 0;
    
    automateCards.forEach(card => {
        const cardType = card.dataset.type;
        // Gérer le cas epsilon-afn qui peut être affiché comme "epsilon" dans le filtre
        const shouldShow = filterType === 'all' || 
                          cardType === filterType || 
                          (filterType === 'epsilon' && cardType === 'epsilon-afn');
        
        if (shouldShow) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Show/hide empty state
    if (visibleCount === 0 && automateCards.length > 0) {
        automatesGrid.style.display = 'none';
        emptyState.style.display = 'block';
        emptyState.querySelector('.empty-title').textContent = 'Aucun automate trouvé';
        emptyState.querySelector('.empty-description').textContent = 
            'Aucun automate ne correspond aux critères de filtrage sélectionnés.';
    } else {
        automatesGrid.style.display = 'grid';
        emptyState.style.display = 'none';
    }
}

function clearFilters() {
    setActiveFilter('all');
    filterAutomates('all');
}

function createAutomate() {
    // Rediriger vers la page de création d'automate
    window.location.href = '/automates/create';
}

// Action handlers améliorés
function handleAction(action, automateId, automateName) {
    switch(action) {
        case 'visualize':
            window.location.href = API_URLS.visualize(automateId);
            break;
        case 'edit':
            window.location.href = API_URLS.edit(automateId);
            break;
        case 'export':
            exportAutomate(automateId, automateName);
            break;
        case 'delete':
            showDeleteModal(automateId, automateName);
            break;
        case 'convert-afd':
            convertAutomate(automateId, 'afd');
            break;
        case 'convert-afn':
            convertAutomate(automateId, 'afn');
            break;
        case 'convert-regex':
            convertAutomate(automateId, 'regex');
            break;
        case 'minimize':
            operateAutomate(automateId, 'minimize');
            break;
        case 'complete':
            operateAutomate(automateId, 'complete');
            break;
        case 'table':
            showAutomateTable(automateId);
            break;
        default:
            showNotification(`Action "${action}" sur l'automate: ${automateName}`, 'info');
    }
}

// Fonctions spécifiques pour les actions
async function exportAutomate(automateId, automateName) {
    try {
        showLoading(`Exportation de ${automateName}...`);
        
        const response = await fetch(API_URLS.export(automateId));
        if (!response.ok) throw new Error('Erreur lors de l\'exportation');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${automateName.replace(/\s+/g, '_')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        hideLoading();
        showNotification(`Automate "${automateName}" exporté avec succès`, 'success');
    } catch (error) {
        hideLoading();
        showNotification(`Erreur lors de l'exportation: ${error.message}`, 'error');
    }
}

async function convertAutomate(automateId, targetType) {
    try {
        showLoading(`Conversion vers ${targetType.toUpperCase()}...`);
        
        const response = await fetch(`/api/automates/${automateId}/convert/${targetType}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Erreur lors de la conversion');
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showNotification(`Conversion vers ${targetType.toUpperCase()} réussie`, 'success');
            // Optionnel: rediriger vers le nouvel automate
            if (result.newAutomateId) {
                setTimeout(() => {
                    window.location.href = API_URLS.visualize(result.newAutomateId);
                }, 1500);
            }
        } else {
            throw new Error(result.error || 'Erreur inconnue');
        }
    } catch (error) {
        hideLoading();
        showNotification(`Erreur lors de la conversion: ${error.message}`, 'error');
    }
}

async function operateAutomate(automateId, operation) {
    try {
        showLoading(`Opération ${operation}...`);
        
        const response = await fetch(`/api/automates/${automateId}/${operation}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`Erreur lors de l'opération ${operation}`);
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showNotification(`Opération ${operation} réussie`, 'success');
            // Recharger la page pour voir les modifications
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(result.error || 'Erreur inconnue');
        }
    } catch (error) {
        hideLoading();
        showNotification(`Erreur lors de l'opération: ${error.message}`, 'error');
    }
}

function showAutomateTable(automateId) {
    window.open(`/automates/${automateId}/table`, '_blank');
}

// Modal de suppression
function showDeleteModal(automateId, automateName) {
    automateToDelete = automateId;
    document.getElementById('deleteAutomateName').textContent = automateName;
    deleteModal.style.display = 'flex';
    deleteModal.style.animation = 'fadeIn 0.3s ease-in';
}

function closeDeleteModal() {
    deleteModal.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => {
        deleteModal.style.display = 'none';
        automateToDelete = null;
    }, 300);
}

async function confirmDelete() {
    if (!automateToDelete) return;
    
    try {
        showLoading('Suppression en cours...');
        
        const response = await fetch(API_URLS.delete(automateToDelete), {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Erreur lors de la suppression');
        
        const result = await response.json();
        
        if (result.success) {
            // Supprimer visuellement la carte
            const card = document.querySelector(`[data-id="${automateToDelete}"]`);
            if (card) {
                card.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    card.remove();
                    updateCounts();
                    // Vérifier s'il faut afficher l'état vide
                    if (document.querySelectorAll('.automate-card').length === 0) {
                        location.reload();
                    }
                }, 300);
            }
            
            hideLoading();
            closeDeleteModal();
            showNotification('Automate supprimé avec succès', 'success');
        } else {
            throw new Error(result.error || 'Erreur inconnue');
        }
    } catch (error) {
        hideLoading();
        closeDeleteModal();
        showNotification(`Erreur lors de la suppression: ${error.message}`, 'error');
    }
}

// Mettre à jour les compteurs après suppression
function updateCounts() {
    const cards = document.querySelectorAll('.automate-card');
    const totalCount = cards.length;
    
    // Mettre à jour le compteur total
    document.querySelector('.stat-number').textContent = totalCount;
    
    // Mettre à jour les compteurs par type
    const typeCounts = {};
    cards.forEach(card => {
        const type = card.dataset.type;
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    
    filterTabs.forEach(tab => {
        const type = tab.dataset.type;
        const countSpan = tab.querySelector('.filter-count');
        if (type === 'all') {
            countSpan.textContent = totalCount;
        } else {
            countSpan.textContent = typeCounts[type] || 0;
        }
    });
}

// Système de notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getIconForType(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Suppression automatique après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Système de loading
function showLoading(message = 'Chargement...') {
    let loader = document.getElementById('loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner"></div>
                <p class="loader-text">${message}</p>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        loader.querySelector('.loader-text').textContent = message;
    }
    loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// Gestionnaire d'événements pour les boutons d'action
function initializeActionButtons() {
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.action-btn');
        if (!btn) return;
        
        const card = btn.closest('.automate-card');
        const automateId = parseInt(card.dataset.id);
        const automateName = card.querySelector('.automate-name').textContent;
        const action = btn.dataset.action;
        
        if (action) {
            e.preventDefault();
            handleAction(action, automateId, automateName);
        }
    });
}

// Recherche en temps réel
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const cards = document.querySelectorAll('.automate-card');
            let visibleCount = 0;
            
            cards.forEach(card => {
                const name = card.querySelector('.automate-name').textContent.toLowerCase();
                const description = card.querySelector('.automate-description').textContent.toLowerCase();
                const shouldShow = name.includes(query) || description.includes(query);
                
                if (shouldShow && (currentFilter === 'all' || card.dataset.type === currentFilter)) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Afficher/masquer l'état vide pour la recherche
            if (visibleCount === 0 && cards.length > 0) {
                automatesGrid.style.display = 'none';
                emptyState.style.display = 'block';
                emptyState.querySelector('.empty-title').textContent = 'Aucun résultat trouvé';
                emptyState.querySelector('.empty-description').textContent = 
                    `Aucun automate ne correspond à votre recherche "${query}".`;
            } else {
                automatesGrid.style.display = 'grid';
                emptyState.style.display = 'none';
            }
        });
    }
}

// Gestion des raccourcis clavier
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+N pour créer un nouvel automate
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            createAutomate();
        }
        
        // Echap pour fermer les modales
        if (e.key === 'Escape') {
            closeDeleteModal();
        }
        
        // Touches numériques pour les filtres
        if (e.key >= '1' && e.key <= '6') {
            const tabs = Array.from(filterTabs);
            const tabIndex = parseInt(e.key) - 1;
            if (tabs[tabIndex]) {
                tabs[tabIndex].click();
            }
        }
    });
}

// Animation des cartes au survol
function initializeCardAnimations() {
    automateCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

// Drag and Drop pour réorganiser les automates
function initializeDragAndDrop() {
    let draggedElement = null;
    
    automateCards.forEach(card => {
        card.draggable = true;
        
        card.addEventListener('dragstart', function(e) {
            draggedElement = this;
            this.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        });
        
        card.addEventListener('dragend', function() {
            this.style.opacity = '';
            draggedElement = null;
        });
        
        card.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
        
        card.addEventListener('drop', function(e) {
            e.preventDefault();
            if (draggedElement && draggedElement !== this) {
                const grid = this.parentNode;
                const afterElement = getDragAfterElement(grid, e.clientY);
                
                if (afterElement == null) {
                    grid.appendChild(draggedElement);
                } else {
                    grid.insertBefore(draggedElement, afterElement);
                }
                
                showNotification('Ordre des automates modifié', 'info');
            }
        });
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.automate-card:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Sauvegarde automatique des préférences utilisateur
function saveUserPreferences() {
    const preferences = {
        currentFilter: currentFilter,
        viewMode: 'grid' // pour une future fonctionnalité
    };
    
    // Utiliser une variable globale au lieu de localStorage
    window.userPreferences = preferences;
}

function loadUserPreferences() {
    const preferences = window.userPreferences || { currentFilter: 'all' };
    
    if (preferences.currentFilter && preferences.currentFilter !== 'all') {
        setActiveFilter(preferences.currentFilter);
        filterAutomates(preferences.currentFilter);
    }
}

// Validation des actions avant exécution
function validateAction(action, automateType) {
    const validActions = {
        'afd': ['visualize', 'edit', 'export', 'delete', 'convert-afn', 'convert-regex', 'minimize', 'complete', 'table'],
        'afn': ['visualize', 'edit', 'export', 'delete', 'convert-afd', 'convert-regex', 'complete', 'table'],
        'epsilon-afn': ['visualize', 'edit', 'export', 'delete', 'convert-afd', 'convert-afn', 'convert-regex', 'complete', 'table'],
        'afdc': ['visualize', 'edit', 'export', 'delete', 'convert-afd', 'convert-afn', 'convert-regex', 'table'],
        'thompson': ['visualize', 'edit', 'export', 'delete', 'convert-afd', 'convert-afn', 'convert-regex', 'table']
    };
    
    return validActions[automateType] && validActions[automateType].includes(action);
}

// Initialisation de tous les composants
function initializeApp() {
    initializeFilters();
    initializeActionButtons();
    initializeSearch();
    initializeKeyboardShortcuts();
    initializeCardAnimations();
    initializeDragAndDrop();
    loadUserPreferences();
    
    // Sauvegarder les préférences lors des changements
    filterTabs.forEach(tab => {
        tab.addEventListener('click', saveUserPreferences);
    });
    
    console.log('Application des automates initialisée avec succès');
}

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    showNotification('Une erreur inattendue s\'est produite', 'error');
});

// Gestion des erreurs de requêtes
window.addEventListener('unhandledrejection', function(e) {
    console.error('Erreur de promesse non gérée:', e.reason);
    showNotification('Erreur de communication avec le serveur', 'error');
});

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', initializeApp);

// Nettoyage lors de la fermeture de la page
window.addEventListener('beforeunload', function() {
    saveUserPreferences();
});


// Fonction pour générer et afficher le graphe réel de chaque automate
function renderAutomateGraphs() {
    // Vérifier que les données sont disponibles
    if (!window.automatesData) {
        console.warn('Aucune donnée d\'automate trouvée dans window.automatesData');
        return;
    }

    const automateCards = document.querySelectorAll('.automate-card');
    
    automateCards.forEach((card) => {
        const automateId = parseInt(card.dataset.id);
        const graphContainer = card.querySelector('.automate-graph');
        
        if (!graphContainer) {
            console.warn(`Container .automate-graph non trouvé pour l'automate ${automateId}`);
            return;
        }
        
        try {
            // Utiliser les données intégrées dans la page
            const automateData = window.automatesData[automateId];
            
            if (automateData && automateData.states && automateData.transitions) {
                // Générer le graphe SVG
                generateAutomateSVG(graphContainer, automateData);
            } else {
                throw new Error(`Données incomplètes pour l'automate ${automateId}`);
            }
            
        } catch (error) {
            console.error(`Erreur lors du rendu du graphe pour l'automate ${automateId}:`, error);
            // Afficher un message d'erreur dans le container
            graphContainer.innerHTML = `
                <div class="graph-error" style="display: flex; align-items: center; justify-content: center; height: 150px; color: #666; flex-direction: column;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 8px;"></i>
                    <span>Erreur de chargement du graphique</span>
                </div>
            `;
        }
    });
}

function generateAutomateSVG(container, automateData) {
    const { states, transitions, alphabet, id } = automateData;
    
    // Vérifications de sécurité
    if (!states || !Array.isArray(states) || states.length === 0) {
        container.innerHTML = '<div class="graph-error">Aucun état défini</div>';
        return;
    }
    
    // Dimensions du SVG
    const width = 350;
    const height = 200;
    const margin = 30;
    
    // Créer l'élément SVG
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.style.overflow = 'visible';
    svg.style.background = '#fafafa';
    svg.style.border = '1px solid #e0e0e0';
    svg.style.borderRadius = '4px';
    
    // Calculer les positions des états
    const positions = calculateStatePositions(states, width - 2 * margin, height - 2 * margin, margin);
    
    // Définir les marqueurs pour les flèches
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', `arrowhead-${id}`);
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '7');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('orient', 'auto');
    marker.setAttribute('markerUnits', 'strokeWidth');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
    polygon.setAttribute('fill', '#555');
    
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    
    // Dessiner les transitions (arêtes) en premier pour qu'elles soient sous les états
    if (transitions && Array.isArray(transitions)) {
        transitions.forEach(transition => {
            const fromPos = positions[transition.from_state];
            const toPos = positions[transition.to_state];
            
            if (fromPos && toPos) {
                drawTransition(svg, fromPos, toPos, transition, id);
            }
        });
    }
    
    // Dessiner les états (nœuds) par-dessus les transitions
    states.forEach(state => {
        const pos = positions[state.state_id];
        if (pos) {
            drawState(svg, pos, state, id);
        }
    });
    
    // Remplacer le contenu du container
    container.innerHTML = '';
    container.appendChild(svg);
}

function calculateStatePositions(states, width, height, margin) {
    const positions = {};
    const numStates = states.length;
    
    if (numStates === 0) return positions;
    
    if (numStates === 1) {
        // Un seul état au centre
        positions[states[0].state_id] = {
            x: margin + width / 2,
            y: margin + height / 2
        };
    } else if (numStates <= 8) {
        // Disposition circulaire pour peu d'états
        const centerX = margin + width / 2;
        const centerY = margin + height / 2;
        const radius = Math.min(width, height) / 3;
        
        states.forEach((state, index) => {
            const angle = (2 * Math.PI * index) / numStates - Math.PI / 2;
            positions[state.state_id] = {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        });
    } else {
        // Disposition en grille pour beaucoup d'états
        const cols = Math.ceil(Math.sqrt(numStates));
        const rows = Math.ceil(numStates / cols);
        const cellWidth = width / cols;
        const cellHeight = height / rows;
        
        states.forEach((state, index) => {
            const col = index % cols;
            const row = Math.floor(index / cols);
            positions[state.state_id] = {
                x: margin + col * cellWidth + cellWidth / 2,
                y: margin + row * cellHeight + cellHeight / 2
            };
        });
    }
    
    return positions;
}

function drawState(svg, position, state, automateId) {
    const stateGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    stateGroup.setAttribute('class', 'state-group');
    
    // Couleurs selon le type d'état
    const fillColor = state.is_initial ? '#e3f2fd' : '#ffffff';
    const strokeColor = state.is_final ? '#4caf50' : '#2196f3';
    const strokeWidth = state.is_final ? 3 : 2;
    
    // Cercle principal
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', position.x);
    circle.setAttribute('cy', position.y);
    circle.setAttribute('r', 18);
    circle.setAttribute('fill', fillColor);
    circle.setAttribute('stroke', strokeColor);
    circle.setAttribute('stroke-width', strokeWidth);
    circle.style.filter = 'drop-shadow(1px 1px 2px rgba(0,0,0,0.1))';
    
    stateGroup.appendChild(circle);
    
    // Double cercle pour les états finaux
    if (state.is_final) {
        const innerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        innerCircle.setAttribute('cx', position.x);
        innerCircle.setAttribute('cy', position.y);
        innerCircle.setAttribute('r', 13);
        innerCircle.setAttribute('fill', 'none');
        innerCircle.setAttribute('stroke', strokeColor);
        innerCircle.setAttribute('stroke-width', 1.5);
        stateGroup.appendChild(innerCircle);
    }
    
    // Flèche d'entrée pour l'état initial
    if (state.is_initial) {
        const arrowLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        arrowLine.setAttribute('x1', position.x - 35);
        arrowLine.setAttribute('y1', position.y);
        arrowLine.setAttribute('x2', position.x - 20);
        arrowLine.setAttribute('y2', position.y);
        arrowLine.setAttribute('stroke', '#555');
        arrowLine.setAttribute('stroke-width', 2);
        arrowLine.setAttribute('marker-end', `url(#arrowhead-${automateId})`);
        stateGroup.appendChild(arrowLine);
    }
    
    // Texte de l'état
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', position.x);
    text.setAttribute('y', position.y + 5);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-size', '12');
    text.setAttribute('font-weight', 'bold');
    text.setAttribute('fill', '#333');
    text.textContent = state.state_id;
    
    stateGroup.appendChild(text);
    svg.appendChild(stateGroup);
}

function drawTransition(svg, fromPos, toPos, transition, automateId) {
    const transitionGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    transitionGroup.setAttribute('class', 'transition-group');
    
    // Calculer les points de connexion sur les cercles
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < 5) {
        // Auto-transition (boucle sur soi-même)
        drawSelfLoop(svg, fromPos, transition, automateId);
        return;
    }
    
    const unitX = dx / distance;
    const unitY = dy / distance;
    
    // Ajuster les points de départ et d'arrivée pour éviter de chevaucher les cercles
    const stateRadius = 18;
    const startX = fromPos.x + unitX * stateRadius;
    const startY = fromPos.y + unitY * stateRadius;
    const endX = toPos.x - unitX * stateRadius;
    const endY = toPos.y - unitY * stateRadius;
    
    // Ligne de transition
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', startX);
    line.setAttribute('y1', startY);
    line.setAttribute('x2', endX);
    line.setAttribute('y2', endY);
    line.setAttribute('stroke', '#555');
    line.setAttribute('stroke-width', 2);
    line.setAttribute('marker-end', `url(#arrowhead-${automateId})`);
    
    transitionGroup.appendChild(line);
    
    // Texte du symbole de transition
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    
    // Décaler le texte perpendiculairement à la ligne
    const perpX = -unitY * 12;
    const perpY = unitX * 12;
    
    // Arrière-plan blanc pour le texte
    const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    const symbol = transition.symbol || 'ε';
    const textWidth = Math.max(16, symbol.length * 8);
    
    textBg.setAttribute('x', midX + perpX - textWidth/2);
    textBg.setAttribute('y', midY + perpY - 8);
    textBg.setAttribute('width', textWidth);
    textBg.setAttribute('height', '16');
    textBg.setAttribute('fill', 'white');
    textBg.setAttribute('stroke', '#ddd');
    textBg.setAttribute('stroke-width', '0.5');
    textBg.setAttribute('rx', '3');
    textBg.style.filter = 'drop-shadow(0px 1px 1px rgba(0,0,0,0.1))';
    
    transitionGroup.appendChild(textBg);
    
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', midX + perpX);
    text.setAttribute('y', midY + perpY + 4);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-size', '10');
    text.setAttribute('font-weight', 'bold');
    text.setAttribute('fill', '#333');
    text.textContent = symbol;
    
    transitionGroup.appendChild(text);
    svg.appendChild(transitionGroup);
}

function drawSelfLoop(svg, position, transition, automateId) {
    const loopGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    loopGroup.setAttribute('class', 'self-loop-group');
    
    // Arc pour la boucle
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const loopRadius = 15;
    const startX = position.x;
    const startY = position.y - 18;
    
    const pathData = `M ${startX} ${startY} 
                     C ${startX - loopRadius} ${startY - loopRadius}, 
                       ${startX + loopRadius} ${startY - loopRadius}, 
                       ${startX} ${startY}`;
    
    path.setAttribute('d', pathData);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#555');
    path.setAttribute('stroke-width', 2);
    path.setAttribute('marker-end', `url(#arrowhead-${automateId})`);
    
    loopGroup.appendChild(path);
    
    // Arrière-plan pour le texte du symbole
    const symbol = transition.symbol || 'ε';
    const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    textBg.setAttribute('x', position.x - 8);
    textBg.setAttribute('y', position.y - 38);
    textBg.setAttribute('width', '16');
    textBg.setAttribute('height', '14');
    textBg.setAttribute('fill', 'white');
    textBg.setAttribute('stroke', '#ddd');
    textBg.setAttribute('stroke-width', '0.5');
    textBg.setAttribute('rx', '3');
    
    loopGroup.appendChild(textBg);
    
    // Texte du symbole
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', position.x);
    text.setAttribute('y', position.y - 28);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-size', '10');
    text.setAttribute('font-weight', 'bold');
    text.setAttribute('fill', '#333');
    text.textContent = symbol;
    
    loopGroup.appendChild(text);
    svg.appendChild(loopGroup);
}

// Fonction pour mettre à jour un graphe spécifique après modification
function updateAutomateGraph(automateId) {
    const card = document.querySelector(`[data-id="${automateId}"]`);
    if (!card) {
        console.warn(`Carte d'automate non trouvée pour l'ID ${automateId}`);
        return;
    }
    
    const graphContainer = card.querySelector('.automate-graph');
    if (!graphContainer) {
        console.warn(`Container de graphique non trouvé pour l'automate ${automateId}`);
        return;
    }
    
    // Tenter d'abord d'utiliser les données en mémoire si elles existent
    if (window.automatesData && window.automatesData[automateId]) {
        try {
            generateAutomateSVG(graphContainer, window.automatesData[automateId]);
            return;
        } catch (error) {
            console.warn('Erreur avec les données en mémoire, tentative de récupération via API:', error);
        }
    }
    
    // Sinon, récupérer via API
    fetch(`/api/automates/${automateId}/graph-data`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(automateData => {
            // Mettre à jour les données en mémoire
            if (!window.automatesData) {
                window.automatesData = {};
            }
            window.automatesData[automateId] = automateData;
            
            // Générer le graphique
            generateAutomateSVG(graphContainer, automateData);
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour du graphe:', error);
            graphContainer.innerHTML = `
                <div class="graph-error" style="display: flex; align-items: center; justify-content: center; height: 150px; color: #666; flex-direction: column;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 8px;"></i>
                    <span>Erreur de mise à jour</span>
                </div>
            `;
        });
}

// Fonction publique pour rafraîchir tous les graphiques
function refreshAllAutomateGraphs() {
    console.log('Rafraîchissement de tous les graphiques d\'automates...');
    renderAutomateGraphs();
}

// Initialiser le rendu des graphiques après le chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un peu pour que les autres éléments soient initialisés
    setTimeout(() => {
        console.log('Initialisation du rendu des graphiques d\'automates...');
        renderAutomateGraphs();
    }, 500);
});

// Gestion du redimensionnement de la fenêtre
window.addEventListener('resize', function() {
    // Debounce pour éviter trop d'appels
    clearTimeout(window.resizeTimeout);
    window.resizeTimeout = setTimeout(renderAutomateGraphs, 300);
});

// Exposer certaines fonctions globalement pour faciliter le debugging
window.automateGraphRenderer = {
    render: renderAutomateGraphs,
    update: updateAutomateGraph,
    refresh: refreshAllAutomateGraphs
};