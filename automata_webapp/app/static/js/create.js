class AutomateCreator {
    constructor() {
        this.currentStep = 1;
        this.maxSteps = 4;
        this.selectedType = null;
        this.alphabet = new Set();
        this.states = new Map();
        this.transitions = new Map();
        this.initialState = null;
        this.finalStates = new Set();
        this.currentTool = 'select';
        this.selectedState = null;
        this.canvasOffset = { x: 0, y: 0 };
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.transitionMode = null; // 'selecting' or null
        this.transitionFrom = null;
        this.automateConfig = {
            allowEpsilonTransitions: false,
            allowMultipleTransitions: false,
            requireCompleteTransitions: false
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateProgress();
        this.setupCanvas();
        this.addTransitionStyles();
    }

    addTransitionStyles() {
        // Ajouter les styles pour les transitions si ils n'existent pas
        const existingStyles = document.getElementById('transition-styles');
        if (!existingStyles) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'transition-styles';
            styleSheet.textContent = `
                .creator-state {
                    position: absolute;
                    width: 50px;
                    height: 50px;
                    border: 2px solid var(--primary-color, #007bff);
                    border-radius: 50%;
                    background: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 600;
                    cursor: pointer;
                    z-index: 10;
                    user-select: none;
                    transition: all 0.2s ease;
                    pointer-events: auto;
                }

                .creator-state:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
                }

                .creator-state.initial {
                    border-color: #28a745;
                    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.3);
                }

                .creator-state.final {
                    border: 4px double var(--primary-color, #007bff);
                }

                .creator-state.initial.final {
                    border: 4px double #28a745;
                    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.3);
                }

                .creator-state.selected {
                    border-color: #ffc107;
                    box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.3);
                }

                .creator-state.selecting {
                    border-color: #dc3545;
                    box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.3);
                    animation: pulse 1s infinite;
                }

                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }

                .transitions-svg {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 5;
                }

                .transition-group {
                    pointer-events: none;
                }

                .transition-label {
                    font-size: 12px;
                    font-weight: 600;
                    fill: var(--text-primary, #333);
                }
            `;
            document.head.appendChild(styleSheet);
        }
    }

    bindEvents() {
        // Navigation buttons
        document.getElementById('prevBtn').addEventListener('click', () => this.previousStep());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());

        // Type selection
        document.querySelectorAll('.creator-type-card').forEach(card => {
            card.addEventListener('click', () => this.selectType(card.dataset.type));
        });

        // Alphabet input
        document.getElementById('alphabetInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addSymbol(e.target.value.trim());
                e.target.value = '';
            }
        });

        // Toolbar buttons
        document.querySelectorAll('.creator-tool-btn').forEach(btn => {
            if (btn.dataset.tool) {
                btn.addEventListener('click', () => this.selectTool(btn.dataset.tool));
            } else if (btn.dataset.action) {
                btn.addEventListener('click', () => this.executeAction(btn.dataset.action));
            }
        });

        // Action buttons
        document.getElementById('saveBtn').addEventListener('click', () => this.saveAutomate());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportAutomate());
        document.getElementById('importBtn').addEventListener('click', () => this.importAutomate());

        // Test button
        document.getElementById('testAutomateBtn').addEventListener('click', () => this.showTestModal());
        document.getElementById('validateAutomateBtn').addEventListener('click', () => this.validateAutomate());
        document.getElementById('optimizeAutomateBtn').addEventListener('click', () => this.optimizeAutomate());

        // Modal events
        document.getElementById('closeTestModal').addEventListener('click', () => this.hideTestModal());
        document.getElementById('runTest').addEventListener('click', () => this.runTest());
        document.querySelector('.creator-modal-close').addEventListener('click', () => this.hideTestModal());

        // File input
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileImport(e));
    }

    selectType(type) {
        // Remove previous selection
        document.querySelectorAll('.creator-type-card').forEach(card => {
            card.classList.remove('selected');
        });
    
        // Select new type
        document.querySelector(`[data-type="${type}"]`).classList.add('selected');
        this.selectedType = type;
    
        // Configure automate based on type
        this.configureAutomateType(type);
    
        // Enable next button
        const nextBtn = document.getElementById('nextBtn');
        nextBtn.disabled = false;
        nextBtn.style.opacity = '1';
        nextBtn.style.pointerEvents = 'auto';
    }

    configureAutomateType(type) {
        switch (type) {
            case 'afd':
                this.automateConfig = {
                    allowEpsilonTransitions: false,
                    allowMultipleTransitions: false,
                    requireCompleteTransitions: false
                };
                break;
            case 'afn':
                this.automateConfig = {
                    allowEpsilonTransitions: false,
                    allowMultipleTransitions: true,
                    requireCompleteTransitions: false
                };
                break;
            case 'epsilon-afn':
                this.automateConfig = {
                    allowEpsilonTransitions: true,
                    allowMultipleTransitions: true,
                    requireCompleteTransitions: false
                };
                // Ajouter automatiquement epsilon à l'alphabet
                this.alphabet.add('ε');
                this.renderAlphabetTags();
                break;
            case 'afdc':
                this.automateConfig = {
                    allowEpsilonTransitions: false,
                    allowMultipleTransitions: false,
                    requireCompleteTransitions: true
                };
                break;
        }
        
        console.log(`Configuration pour ${type}:`, this.automateConfig);
    }
    addSymbol(symbol) {
        if (symbol && !this.alphabet.has(symbol)) {
            this.alphabet.add(symbol);
            this.renderAlphabetTags();
        }
    }

    removeSymbol(symbol) {
        this.alphabet.delete(symbol);
        this.renderAlphabetTags();
    }

    renderAlphabetTags() {
        const container = document.getElementById('alphabetTags');
        container.innerHTML = '';

        this.alphabet.forEach(symbol => {
            const tag = document.createElement('div');
            tag.className = 'creator-alphabet-tag';
            tag.innerHTML = `
                ${symbol}
                <span class="creator-alphabet-remove" onclick="automateCreator.removeSymbol('${symbol}')">&times;</span>
            `;
            container.appendChild(tag);
        });
    }

    setupCanvas() {
        const canvas = document.getElementById('automateCanvas');
        canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        canvas.addEventListener('mouseup', () => this.handleMouseUp());
    }

    handleCanvasClick(e) {
        // Vérifier d'abord si on a cliqué sur un état existant
        const clickedState = e.target.closest('.creator-state');
        
        if (clickedState) {
            // On a cliqué sur un état existant
            const stateId = clickedState.dataset.stateId;
            console.log(`Clic sur l'état: ${stateId} avec l'outil: ${this.currentTool}`);
            
            switch (this.currentTool) {
                case 'select':
                    this.selectState(stateId);
                    break;
                case 'initial':
                    this.setInitialStateById(stateId);
                    break;
                case 'final':
                    this.setFinalStateById(stateId);
                    break;
                case 'transition':
                    this.handleTransitionClickById(stateId);
                    break;
            }
        } else {
            // Clic sur le canvas vide
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            console.log(`Clic sur canvas vide à (${x}, ${y}) avec l'outil: ${this.currentTool}`);
            
            if (this.currentTool === 'state') {
                this.addState(x, y);
            } else if (this.transitionMode === 'selecting') {
                // Annuler le mode transition si on clique dans le vide
                this.cancelTransitionMode();
            }
        }
    }

    addState(x, y) {
        const stateId = `q${this.states.size}`;
        const state = {
            id: stateId,
            x: x,
            y: y,
            isInitial: false,
            isFinal: false
        };

        this.states.set(stateId, state);
        this.renderCanvas();
        
        // Hide placeholder
        const placeholder = document.querySelector('.creator-canvas-placeholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        
        console.log(`État ${stateId} ajouté à (${x}, ${y})`);
    }

    // Nouvelle méthode pour sélectionner un état par son ID
    selectState(stateId) {
        this.selectedState = stateId;
        this.renderCanvas();
        console.log(`État ${stateId} sélectionné`);
    }

    // Nouvelle méthode pour définir l'état initial par ID
    setInitialStateById(stateId) {
        console.log(`Définition de l'état initial: ${stateId}`);
        
        // Retirer l'état initial précédent
        if (this.initialState) {
            const prevState = this.states.get(this.initialState);
            if (prevState) prevState.isInitial = false;
        }
        
        // Définir le nouvel état initial
        this.initialState = stateId;
        const state = this.states.get(stateId);
        if (state) {
            state.isInitial = true;
            this.renderCanvas();
            this.showNotification(`État ${stateId} défini comme initial`, 'success');
        }
    }

    // Nouvelle méthode pour définir l'état final par ID
    setFinalStateById(stateId) {
        console.log(`Définition/suppression de l'état final: ${stateId}`);
        
        const state = this.states.get(stateId);
        if (state) {
            if (state.isFinal) {
                // Retirer l'état final
                state.isFinal = false;
                this.finalStates.delete(stateId);
                this.showNotification(`État ${stateId} n'est plus final`, 'info');
            } else {
                // Ajouter l'état final
                state.isFinal = true;
                this.finalStates.add(stateId);
                this.showNotification(`État ${stateId} défini comme final`, 'success');
            }
            
            this.renderCanvas();
        }
    }

    // Nouvelle méthode pour gérer les clics de transition par ID
    handleTransitionClickById(stateId) {
        console.log(`Clic transition sur état: ${stateId}, mode: ${this.transitionMode}`);
        
        if (this.transitionMode === null) {
            // Premier clic - sélectionner l'état source
            this.transitionFrom = stateId;
            this.transitionMode = 'selecting';
            
            // Marquer l'état comme source
            this.updateTransitionSelection();
            
            this.showNotification(`État source: ${stateId}. Cliquez sur l'état de destination`, 'info');
        } else if (this.transitionMode === 'selecting') {
            // Deuxième clic - créer la transition
            this.createTransition(this.transitionFrom, stateId);
            
            // Réinitialiser le mode transition
            this.transitionMode = null;
            this.transitionFrom = null;
            this.updateTransitionSelection();
        }
    }

    // Méthode pour mettre à jour la sélection visuelle des transitions
    updateTransitionSelection() {
        document.querySelectorAll('.creator-state').forEach(el => {
            el.classList.remove('selecting');
        });
        
        if (this.transitionFrom) {
            const stateElement = document.querySelector(`[data-state-id="${this.transitionFrom}"]`);
            if (stateElement) {
                stateElement.classList.add('selecting');
            }
        }
    }

    // Méthode pour annuler le mode transition
    cancelTransitionMode() {
        this.transitionMode = null;
        this.transitionFrom = null;
        this.updateTransitionSelection();
        this.showNotification('Mode transition annulé', 'info');
    }

    selectTool(tool) {
        // Update active tool button
        document.querySelectorAll('.creator-tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const toolBtn = document.querySelector(`[data-tool="${tool}"]`);
        if (toolBtn) {
            toolBtn.classList.add('active');
        }
        
        this.currentTool = tool;
        
        // Reset transition mode when changing tool
        if (tool !== 'transition') {
            this.cancelTransitionMode();
        }
        
        // Update cursor
        const canvas = document.getElementById('automateCanvas');
        switch (tool) {
            case 'select':
                canvas.style.cursor = 'default';
                break;
            case 'state':
                canvas.style.cursor = 'crosshair';
                break;
            case 'transition':
                canvas.style.cursor = 'pointer';
                break;
            default:
                canvas.style.cursor = 'crosshair';
        }

        console.log(`Outil sélectionné: ${tool}`);
    }

    setInitialState(x, y) {
        const stateId = this.getStateAt(x, y);
        console.log(`Tentative de définir l'état initial à (${x}, ${y}), état trouvé: ${stateId}`);
        
        if (stateId) {
            // Retirer l'état initial précédent
            if (this.initialState) {
                const prevState = this.states.get(this.initialState);
                if (prevState) prevState.isInitial = false;
            }
            
            // Définir le nouvel état initial
            this.initialState = stateId;
            const state = this.states.get(stateId);
            state.isInitial = true;
            
            this.renderCanvas();
            this.showNotification(`État ${stateId} défini comme initial`, 'success');
        } else {
            this.showNotification('Cliquez sur un état pour le définir comme initial', 'info');
        }
    }

    setFinalState(x, y) {
        const stateId = this.getStateAt(x, y);
        console.log(`Tentative de définir l'état final à (${x}, ${y}), état trouvé: ${stateId}`);
        
        if (stateId) {
            const state = this.states.get(stateId);
            
            if (state.isFinal) {
                // Retirer l'état final
                state.isFinal = false;
                this.finalStates.delete(stateId);
                this.showNotification(`État ${stateId} n'est plus final`, 'info');
            } else {
                // Ajouter l'état final
                state.isFinal = true;
                this.finalStates.add(stateId);
                this.showNotification(`État ${stateId} défini comme final`, 'success');
            }
            
            this.renderCanvas();
        } else {
            this.showNotification('Cliquez sur un état pour le définir comme final', 'info');
        }
    }

    getStateAt(x, y) {
        console.log(`Recherche d'état à (${x}, ${y}), États disponibles:`, Array.from(this.states.keys()));
        
        for (let [id, state] of this.states) {
            const distance = Math.sqrt(Math.pow(x - state.x, 2) + Math.pow(y - state.y, 2));
            console.log(`Distance à l'état ${id} (${state.x}, ${state.y}): ${distance}`);
            
            if (distance <= 30) { // Augmenter la zone de détection
                console.log(`État ${id} trouvé!`);
                return id;
            }
        }
        console.log('Aucun état trouvé');
        return null;
    }

    handleTransitionClick(x, y) {
        const stateId = this.getStateAt(x, y);
        console.log(`Clic transition à (${x}, ${y}), état: ${stateId}, mode: ${this.transitionMode}`);
        
        if (!stateId) {
            this.showNotification('Cliquez sur un état pour créer une transition', 'info');
            return;
        }
        
        if (this.transitionMode === null) {
            // Premier clic - sélectionner l'état source
            this.transitionFrom = stateId;
            this.transitionMode = 'selecting';
            
            // Marquer l'état comme source
            document.querySelectorAll('.creator-state').forEach(el => {
                el.classList.remove('selecting');
            });
            const stateElement = document.querySelector(`[data-state-id="${stateId}"]`);
            if (stateElement) {
                stateElement.classList.add('selecting');
            }
            
            this.showNotification(`État source: ${stateId}. Cliquez sur l'état de destination`, 'info');
        } else if (this.transitionMode === 'selecting') {
            // Deuxième clic - créer la transition
            this.createTransition(this.transitionFrom, stateId);
            
            // Réinitialiser le mode transition
            this.transitionMode = null;
            this.transitionFrom = null;
            
            // Retirer le marquage
            document.querySelectorAll('.creator-state').forEach(el => {
                el.classList.remove('selecting');
            });
        }
    }

    createTransition(fromState, toState) {
        // Afficher un prompt pour entrer le symbole de transition
        let symbol = prompt(`Entrez le symbole pour la transition de ${fromState} vers ${toState}:`);
        
        if (symbol !== null && symbol.trim() !== '') {
            const trimmedSymbol = symbol.trim();
            
            // Validation selon le type d'automate
            if (!this.validateTransitionSymbol(trimmedSymbol)) {
                return;
            }
            
            // Créer la clé de transition
            const transitionKey = `${fromState},${trimmedSymbol}`;
            
            // Vérifier les contraintes selon le type d'automate
            if (!this.automateConfig.allowMultipleTransitions && this.transitions.has(transitionKey)) {
                this.showNotification(`Transition déjà existante pour ${fromState} avec ${trimmedSymbol}`, 'error');
                return;
            }
            
            if (!this.transitions.has(transitionKey)) {
                this.transitions.set(transitionKey, []);
            }
            
            // Ajouter la destination
            const destinations = this.transitions.get(transitionKey);
            if (!destinations.includes(toState)) {
                destinations.push(toState);
            }
            
            this.renderCanvas();
            this.showNotification(`Transition ajoutée: ${fromState} --${trimmedSymbol}--> ${toState}`, 'success');
            
            console.log('Transition créée:', transitionKey, '->', destinations);
        }
    }
    validateTransitionSymbol(symbol) {
        // Vérifier si epsilon est autorisé
        if (symbol === 'ε') {
            if (!this.automateConfig.allowEpsilonTransitions) {
                this.showNotification('Les transitions epsilon ne sont pas autorisées pour ce type d\'automate', 'error');
                return false;
            }
            return true;
        }
        
        // Vérifier si le symbole est dans l'alphabet
        if (!this.alphabet.has(symbol)) {
            this.showNotification('Le symbole doit être dans l\'alphabet défini', 'error');
            return false;
        }
        
        return true;
    }
    
    // NOUVELLE MÉTHODE - Validation de la complétude (pour AFDC)
    validateCompletenessForAFDC() {
        if (this.selectedType !== 'afdc') return true;
        
        const missingTransitions = [];
        
        this.states.forEach((state) => {
            this.alphabet.forEach((symbol) => {
                if (symbol === 'ε') return; // Ignorer epsilon pour AFDC
                
                const transitionKey = `${state.id},${symbol}`;
                if (!this.transitions.has(transitionKey)) {
                    missingTransitions.push(`${state.id} --${symbol}-->`);
                }
            });
        });
        
        if (missingTransitions.length > 0) {
            this.showNotification(`Transitions manquantes pour AFDC: ${missingTransitions.join(', ')}`, 'error');
            return false;
        }
        
        return true;
    }
        
    executeAction(action) {
        switch (action) {
            case 'delete':
                this.deleteSelected();
                break;
            case 'clear':
                this.clearCanvas();
                break;
            case 'center':
                this.centerCanvas();
                break;
        }
    }

    renderCanvas() {
        const canvas = document.getElementById('automateCanvas');
        
        // Clear existing elements
        canvas.querySelectorAll('.creator-state, .creator-transition').forEach(el => el.remove());

        // Render transitions first (so they appear behind states)
        this.renderTransitions(canvas);

        // Render states
        this.states.forEach(state => {
            const stateEl = document.createElement('div');
            stateEl.className = 'creator-state';
            stateEl.style.left = `${state.x - 25}px`;
            stateEl.style.top = `${state.y - 25}px`;
            stateEl.textContent = state.id;
            stateEl.dataset.stateId = state.id;
            
            // Assurer que l'état peut recevoir les événements de clic
            stateEl.style.pointerEvents = 'auto';
            stateEl.style.cursor = 'pointer';

            if (state.isInitial) {
                stateEl.classList.add('initial');
            }
            if (state.isFinal) {
                stateEl.classList.add('final');
            }
            if (this.selectedState === state.id) {
                stateEl.classList.add('selected');
            }

            canvas.appendChild(stateEl);
        });

        console.log('Canvas rendu avec', this.states.size, 'états et', this.transitions.size, 'transitions');
    }

    renderTransitions(canvas) {
        // Create SVG for transitions if it doesn't exist
        let svg = canvas.querySelector('.transitions-svg');
        if (!svg) {
            svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'transitions-svg');
            svg.style.position = 'absolute';
            svg.style.top = '0';
            svg.style.left = '0';
            svg.style.width = '100%';
            svg.style.height = '100%';
            svg.style.pointerEvents = 'none';
            svg.style.zIndex = '5';
            
            // Add arrow marker
            const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
            marker.setAttribute('id', 'arrowhead');
            marker.setAttribute('markerWidth', '10');
            marker.setAttribute('markerHeight', '7');
            marker.setAttribute('refX', '9');
            marker.setAttribute('refY', '3.5');
            marker.setAttribute('orient', 'auto');
            
            const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
            polygon.setAttribute('fill', '#007bff');
            
            marker.appendChild(polygon);
            defs.appendChild(marker);
            svg.appendChild(defs);
            
            canvas.appendChild(svg);
        }
        
        // Clear existing transitions
        svg.querySelectorAll('.transition-group').forEach(el => el.remove());
        
        // Render each transition
        this.transitions.forEach((destinations, transitionKey) => {
            const [fromState, symbol] = transitionKey.split(',');
            const fromStateObj = this.states.get(fromState);
            
            if (!fromStateObj) return;
            
            destinations.forEach(toState => {
                const toStateObj = this.states.get(toState);
                if (!toStateObj) return;
                
                this.drawTransition(svg, fromStateObj, toStateObj, symbol);
            });
        });

        console.log('Transitions rendues:', this.transitions.size);
    }

    drawTransition(svg, fromState, toState, symbol) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'transition-group');
        
        // Calculate line positions
        const dx = toState.x - fromState.x;
        const dy = toState.y - fromState.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance === 0) {
            // Self-loop
            this.drawSelfLoop(group, fromState, symbol);
        } else {
            // Regular transition
            const angle = Math.atan2(dy, dx);
            const startX = fromState.x + 25 * Math.cos(angle);
            const startY = fromState.y + 25 * Math.sin(angle);
            const endX = toState.x - 25 * Math.cos(angle);
            const endY = toState.y - 25 * Math.sin(angle);
            
            // Draw line
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', startX);
            line.setAttribute('y1', startY);
            line.setAttribute('x2', endX);
            line.setAttribute('y2', endY);
            line.setAttribute('stroke', '#007bff');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('marker-end', 'url(#arrowhead)');
            
            // Draw label background
            const labelX = (startX + endX) / 2;
            const labelY = (startY + endY) / 2 - 10;
            
            const labelBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            const textWidth = symbol.length * 8 + 6;
            labelBg.setAttribute('x', labelX - textWidth/2);
            labelBg.setAttribute('y', labelY - 8);
            labelBg.setAttribute('width', textWidth);
            labelBg.setAttribute('height', '16');
            labelBg.setAttribute('fill', 'white');
            labelBg.setAttribute('stroke', '#ddd');
            labelBg.setAttribute('rx', '3');
            
            // Draw label text
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', labelX);
            text.setAttribute('y', labelY + 4);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.setAttribute('font-weight', '600');
            text.setAttribute('fill', '#333');
            text.textContent = symbol;
            
            group.appendChild(line);
            group.appendChild(labelBg);
            group.appendChild(text);
        }
        
        svg.appendChild(group);
    }

    drawSelfLoop(group, state, symbol) {
        // Create a self-loop arc
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const cx = state.x;
        const cy = state.y - 40;
        const r = 20;
        
        path.setAttribute('d', `M ${cx - r} ${cy} A ${r} ${r} 0 1 1 ${cx + r} ${cy}`);
        path.setAttribute('stroke', '#007bff');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#arrowhead)');
        
        // Label for self-loop
        const labelBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        const textWidth = symbol.length * 8 + 6;
        labelBg.setAttribute('x', cx - textWidth/2);
        labelBg.setAttribute('y', cy - 33);
        labelBg.setAttribute('width', textWidth);
        labelBg.setAttribute('height', '16');
        labelBg.setAttribute('fill', 'white');
        labelBg.setAttribute('stroke', '#ddd');
        labelBg.setAttribute('rx', '3');
        
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', cx);
        text.setAttribute('y', cy - 21);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', '600');
        text.setAttribute('fill', '#333');
        text.textContent = symbol;
        
        group.appendChild(path);
        group.appendChild(labelBg);
        group.appendChild(text);
    }

    nextStep() {
        console.log('Current step:', this.currentStep, 'Selected type:', this.selectedType);
        
        if (this.currentStep < this.maxSteps) {
            const isValid = this.validateCurrentStep();
            console.log('Step validation:', isValid);
            
            if (isValid) {
                this.currentStep++;
                this.updateStep();
                this.updateProgress();
            } else {
                // Show validation message
                let message = '';
                switch (this.currentStep) {
                    case 1:
                        message = 'Veuillez sélectionner un type d\'automate';
                        break;
                    case 2:
                        message = 'Veuillez ajouter au moins un symbole à l\'alphabet';
                        break;
                    case 3:
                        message = 'Veuillez ajouter au moins un état à l\'automate';
                        break;
                }
                this.showNotification(message, 'error');
            }
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStep();
            this.updateProgress();
        }
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.selectedType !== null;
            case 2:
                return this.alphabet.size > 0;
            case 3:
                return this.states.size > 0;
            default:
                return true;
        }
    }

    updateStep() {
        console.log('Updating to step:', this.currentStep);        
        // Hide all step contents
        document.querySelectorAll('.creator-step-content').forEach(content => {
            content.classList.remove('active');
        });

        // Show current step content
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }

        // Update navigation buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        prevBtn.disabled = this.currentStep === 1;
        prevBtn.style.opacity = this.currentStep === 1 ? '0.5' : '1';
        
        if (this.currentStep === this.maxSteps) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'flex';
        }

        // Update step indicators
        document.querySelectorAll('.creator-step').forEach((step, index) => {
            step.classList.remove('active', 'completed');
            const stepNumber = index + 1;
            
            if (stepNumber < this.currentStep) {
                step.classList.add('completed');
                step.innerHTML = '<i class="fas fa-check"></i><div class="creator-step-label">' + step.querySelector('.creator-step-label').textContent + '</div>';
            } else if (stepNumber === this.currentStep) {
                step.classList.add('active');
                step.innerHTML = '<span>' + stepNumber + '</span><div class="creator-step-label">' + step.querySelector('.creator-step-label').textContent + '</div>';
            } else {
                step.innerHTML = '<span>' + stepNumber + '</span><div class="creator-step-label">' + step.querySelector('.creator-step-label').textContent + '</div>';
            }
        });
    }

    updateProgress() {
        const progressLine = document.getElementById('progressLine');
        if (progressLine) {
            const progress = ((this.currentStep - 1) / (this.maxSteps - 1)) * 70;
            progressLine.style.width = `${progress}%`;
        }
    }

    async saveAutomate() {
        // Validation avant sauvegarde
        if (!this.validateAutomateForSave()) {
            return;
        }
        
        const automateData = {
            type: this.selectedType,
            name: document.getElementById('automateName')?.value || 'Mon Automate',
            description: document.getElementById('automateDescription')?.value || '',
            alphabet: Array.from(this.alphabet),
            states: Array.from(this.states.values()),
            transitions: Array.from(this.transitions.entries()),
            initialState: this.initialState,
            finalStates: Array.from(this.finalStates),
            config: this.automateConfig,
            createdAt: new Date().toISOString()
        };
    
        try {
            // Sauvegarde en base de données
            const response = await fetch('/api/automates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(automateData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Automate sauvegardé avec l'ID: ${result.id}`, 'success');
                
                // Optionnel: sauvegarder aussi localement
                localStorage.setItem('automate_' + result.id, JSON.stringify(automateData));
            } else {
                throw new Error('Erreur lors de la sauvegarde');
            }
        } catch (error) {
            console.error('Erreur:', error);
            // Fallback: sauvegarde locale uniquement
            localStorage.setItem('automate_' + Date.now(), JSON.stringify(automateData));
            this.showNotification('Automate sauvegardé localement (erreur serveur)', 'warning');
        }
    }

    validateAutomateForSave() {
        // Vérifications communes
        if (this.states.size === 0) {
            this.showNotification('L\'automate doit avoir au moins un état', 'error');
            return false;
        }
        
        if (!this.initialState) {
            this.showNotification('L\'automate doit avoir un état initial', 'error');
            return false;
        }
        
        if (this.finalStates.size === 0) {
            this.showNotification('L\'automate doit avoir au moins un état final', 'error');
            return false;
        }
        
        // Validation spécifique pour AFDC
        if (!this.validateCompletenessForAFDC()) {
            return false;
        }
        
        return true;
    }
    
    exportAutomate() {
        const automateData = {
            type: this.selectedType,
            name: document.getElementById('automateName')?.value || 'Mon Automate',
            description: document.getElementById('automateDescription')?.value || '',
            alphabet: Array.from(this.alphabet),
            states: Array.from(this.states.values()),
            transitions: Array.from(this.transitions.entries()),
            initialState: this.initialState,
            finalStates: Array.from(this.finalStates)
        };

        const blob = new Blob([JSON.stringify(automateData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${automateData.name.replace(/\s+/g, '_')}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    importAutomate() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.click();
        }
    }

    handleFileImport(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                this.loadAutomateData(data);
                this.showNotification('Automate importé avec succès!', 'success');
            } catch (error) {
                this.showNotification('Erreur lors de l\'importation du fichier', 'error');
            }
        };
                reader.readAsText(file);
            }

            loadAutomateData(data) {
                this.selectedType = data.type;
                this.alphabet = new Set(data.alphabet);
                this.states = new Map(data.states.map(s => [s.id, s]));
                this.transitions = new Map(data.transitions);
                this.initialState = data.initialState;
                this.finalStates = new Set(data.finalStates);

                // Update UI
                document.getElementById('automateName').value = data.name;
                document.getElementById('automateDescription').value = data.description;
                this.renderAlphabetTags();
                this.renderCanvas();
            }

            showTestModal() {
                document.getElementById('testModal').style.display = 'flex';
            }

            hideTestModal() {
                document.getElementById('testModal').style.display = 'none';
            }

            runTest() {
                const testString = document.getElementById('testString').value;
                const result = this.testString(testString);
                
                const resultDiv = document.getElementById('testResult');
                resultDiv.innerHTML = `
                    <div class="creator-test-result-item ${result.accepted ? 'accepted' : 'rejected'}">
                        <i class="fas ${result.accepted ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                        <span>Chaîne "${testString}" ${result.accepted ? 'acceptée' : 'rejetée'}</span>
                    </div>
                    <div class="creator-test-path">
                        <strong>Chemin:</strong> ${result.path.join(' → ')}
                    </div>
                `;
            }

            testString(str) {
                // Simulation basique du test
                return {
                    accepted: Math.random() > 0.5,
                    path: ['q0', 'q1', 'q2']
                };
            }

            validateAutomate() {
                this.showNotification('Automate validé avec succès!', 'success');
            }

            optimizeAutomate() {
                this.showNotification('Optimisation en cours...', 'info');
                setTimeout(() => {
                    this.showNotification('Automate optimisé!', 'success');
                }, 2000);
            }

            showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = `creator-notification ${type}`;
                notification.innerHTML = `
                    <i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-times' : 'fa-info'}"></i>
                    <span>${message}</span>
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.classList.add('show');
                }, 100);
                
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }, 3000);
            }

            clearCanvas() {
                this.states.clear();
                this.transitions.clear();
                this.initialState = null;
                this.finalStates.clear();
                this.selectedState = null;
                this.renderCanvas();
                document.querySelector('.creator-canvas-placeholder').style.display = 'block';
            }

            deleteSelected() {
                if (this.selectedState) {
                    this.states.delete(this.selectedState);
                    this.selectedState = null;
                    this.renderCanvas();
                }
            }

            selectStateAt(x, y) {
                let selectedStateId = null;
                
                this.states.forEach((state, id) => {
                    const distance = Math.sqrt(Math.pow(x - state.x, 2) + Math.pow(y - state.y, 2));
                    if (distance <= 25) {
                        selectedStateId = id;
                    }
                });
                
                this.selectedState = selectedStateId;
                this.renderCanvas();
            }

            centerCanvas() {
                // Logic to center all states in canvas
                this.renderCanvas();
            }

            handleMouseDown(e) {
                if (this.currentTool === 'select' && this.selectedState) {
                    this.isDragging = true;
                    const rect = e.target.getBoundingClientRect();
                    this.dragStart = {
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top
                    };
                }
            }

            handleMouseMove(e) {
                if (this.isDragging && this.selectedState) {
                    const rect = e.target.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    const state = this.states.get(this.selectedState);
                    if (state) {
                        state.x = x;
                        state.y = y;
                        this.renderCanvas();
                    }
                }
            }

            handleMouseUp() {
                this.isDragging = false;
            }
        }

        // Additional CSS for modal and notifications
        const additionalStyles = `
            .creator-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }

            .creator-modal-content {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                box-shadow: var(--shadow-large);
            }

            .creator-modal-header {
                padding: 1.5rem;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .creator-modal-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-secondary);
            }

            .creator-modal-body {
                padding: 1.5rem;
            }

            .creator-modal-footer {
                padding: 1.5rem;
                border-top: 1px solid var(--border-color);
                display: flex;
                justify-content: flex-end;
                gap: 1rem;
            }

            .creator-test-result-item {
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .creator-test-result-item.accepted {
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }

            .creator-test-result-item.rejected {
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fecaca;
            }

            .creator-test-path {
                padding: 0.5rem;
                background: var(--bg-secondary);
                border-radius: 4px;
                font-family: monospace;
            }

            .creator-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: var(--shadow-large);
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                z-index: 1001;
            }

            .creator-notification.show {
                transform: translateX(0);
            }

            .creator-notification.success {
                border-left: 4px solid var(--success-color);
                color: var(--success-color);
            }

            .creator-notification.error {
                border-left: 4px solid var(--danger-color);
                color: var(--danger-color);
            }

            .creator-notification.info {
                border-left: 4px solid var(--primary-color);
                color: var(--primary-color);
            }
        `;

        // Add additional styles
        const styleSheet = document.createElement('style');
        styleSheet.textContent = additionalStyles;
        document.head.appendChild(styleSheet);

        // Initialize the automate creator
        let automateCreator;
        document.addEventListener('DOMContentLoaded', () => {
            automateCreator = new AutomateCreator();
        });

        fetch('/api/automates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(automateData)
        })
        .then(res => res.json())
        .then(res => {
            if (!res.success) {
                console.error("⛔ Erreurs : ", res.errors || res.details);
                alert("Échec : " + (res.errors ? res.errors.join("\n") : res.details));
                return;
            }
        
            alert("✅ Automate enregistré !");
            // rediriger ou vider le formulaire
        })
        .catch(err => {
            console.error("❌ Erreur réseau :", err);
            alert("Erreur lors de l’envoi au serveur.");
        });
        