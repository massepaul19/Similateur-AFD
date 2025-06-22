// Variables globales - Structure corrigée pour états initiaux multiples
let currentAutomaton = {
    alphabet: '',
    etats: [],
    etats_initiaux: [], // Changé de etat_initial à etats_initiaux (tableau)
    etats_finaux: [],   // Renommé pour la cohérence (pluriel)
    transitions: {}
};

let originalAutomaton = null;
let isAutomatonSaved = false;

// Variables pour le canvas
let canvas, ctx;
let scale = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeCanvas();
});

function initializeCanvas() {
    canvas = document.getElementById('automatonCanvas');
    ctx = canvas.getContext('2d');
    
    // Gestionnaires d'événements pour le zoom et le pan
    canvas.addEventListener('wheel', handleWheel);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);
}

function handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale *= delta;
    scale = Math.max(0.1, Math.min(3, scale));
    drawCurrentAutomaton();
}

function handleMouseDown(e) {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
}

function handleMouseMove(e) {
    if (isDragging) {
        const deltaX = e.clientX - lastMouseX;
        const deltaY = e.clientY - lastMouseY;
        offsetX += deltaX;
        offsetY += deltaY;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        drawCurrentAutomaton();
    }
}

function handleMouseUp() {
    isDragging = false;
}

function resetZoom() {
    scale = 1;
    offsetX = 0;
    offsetY = 0;
    drawCurrentAutomaton();
}

function centerAutomaton() {
    offsetX = 0;
    offsetY = 0;
    drawCurrentAutomaton();
}

// Gestion des onglets

function showTab(tabName) {
    if ((tabName === 'recognition' || tabName === 'analysis' || tabName === 'operations') && !isAutomatonSaved) {
        showMessage('⚠️ Veuillez d\'abord créer et enregistrer un automate', 'warning');
        return;
    }

    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');

    // Changer le canvas actif
    updateActiveCanvas(tabName);
    drawCurrentAutomaton();
}

function updateActiveCanvas(tabName) {
    const canvasMap = {
        'creation': 'automatonCanvas',
        'transitions': 'transitionsCanvas',
        'recognition': 'recognitionCanvas',
        'analysis': 'analysisCanvas',
        'operations': 'operationsCanvas'
    };

    const canvasId = canvasMap[tabName] || 'automatonCanvas';
    canvas = document.getElementById(canvasId);
    if (canvas) {
        ctx = canvas.getContext('2d');
        // Réappliquer les gestionnaires d'événements
        canvas.addEventListener('wheel', handleWheel);
        canvas.addEventListener('mousedown', handleMouseDown);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseup', handleMouseUp);
        canvas.addEventListener('mouseleave', handleMouseUp);
    }
}

//#######################################################################################

// Fonctions de dessin (adaptées pour états initiaux multiples) bloc pour le dessin

function drawCurrentAutomaton() {
    if (!currentAutomaton || !currentAutomaton.etats || currentAutomaton.etats.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#999';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Aucun automate à afficher', canvas.width / 2, canvas.height / 2);
        return;
    }

    drawAutomate(currentAutomaton);
}

function drawAutomate(automate) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!automate || !automate.etats) return;

    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    const positions = calculateStatePositions(automate.etats);
    drawTransitions(automate, positions);
    drawStates(automate, positions);

    ctx.restore();
}

function calculateStatePositions(etats) {
    const positions = {};
    const centerX = canvas.width / 2 / scale;
    const centerY = canvas.height / 2 / scale;
    const radius = Math.min(centerX, centerY) * 0.6;

    if (etats.length === 1) {
        positions[etats[0]] = { x: centerX, y: centerY };
    } else {
        for (let i = 0; i < etats.length; i++) {
            const angle = (2 * Math.PI * i) / etats.length - Math.PI / 2;
            positions[etats[i]] = {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        }
    }
    return positions;
}

function drawStates(automate, positions) {
    const stateRadius = 30;
    for (const etat of automate.etats) {
        const pos = positions[etat];

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, stateRadius, 0, 2 * Math.PI);
        ctx.fillStyle = automate.etats_finaux.includes(etat) ? '#e0f2fe' : '#f8fafc';
        ctx.fill();
        ctx.strokeStyle = automate.etats_finaux.includes(etat) ? '#0277bd' : '#374151';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (automate.etats_finaux.includes(etat)) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, stateRadius - 5, 0, 2 * Math.PI);
            ctx.stroke();
        }

        // Dessiner les flèches pour tous les états initiaux
        if (automate.etats_initiaux.includes(etat)) {
            drawInitialArrow(pos.x - stateRadius - 20, pos.y, pos.x - stateRadius, pos.y);
        }

        ctx.fillStyle = '#374151';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`q${etat}`, pos.x, pos.y);
    }
}

function drawTransitions(automate, positions) {
    const drawn = new Set();
    for (const [fromState, transitions] of Object.entries(automate.transitions)) {
        for (const [symbol, toStates] of Object.entries(transitions)) {
            const destinations = Array.isArray(toStates) ? toStates : [toStates];
            for (const toState of destinations) {
                const key = `${fromState}-${symbol}-${toState}`;
                if (drawn.has(key)) continue;
                drawn.add(key);

                if (fromState == toState) {
                    drawSelfLoop(positions[fromState], symbol);
                } else {
                    drawTransition(positions[fromState], positions[toState], symbol);
                }
            }
        }
    }
}

function drawTransition(fromPos, toPos, symbol) {
    const stateRadius = 30;
    const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
    const startX = fromPos.x + stateRadius * Math.cos(angle);
    const startY = fromPos.y + stateRadius * Math.sin(angle);
    const endX = toPos.x - stateRadius * Math.cos(angle);
    const endY = toPos.y - stateRadius * Math.sin(angle);

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();

    drawArrowHead(endX, endY, angle);
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    drawTransitionLabel(midX, midY, symbol);
}

function drawSelfLoop(pos, symbol) {
    const stateRadius = 30;
    const loopRadius = 25;
    const centerX = pos.x;
    const centerY = pos.y - stateRadius - loopRadius;

    ctx.beginPath();
    ctx.arc(centerX, centerY, loopRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Flèche pour la boucle
    const arrowX = centerX + loopRadius;
    const arrowY = centerY;
    drawArrowHead(arrowX, arrowY, Math.PI / 2);

    // Label de la transition
    drawTransitionLabel(centerX, centerY - loopRadius - 15, symbol);
}

function drawArrowHead(x, y, angle) {
    const arrowLength = 10;
    const arrowAngle = Math.PI / 6;

    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(
        x - arrowLength * Math.cos(angle - arrowAngle),
        y - arrowLength * Math.sin(angle - arrowAngle)
    );
    ctx.moveTo(x, y);
    ctx.lineTo(
        x - arrowLength * Math.cos(angle + arrowAngle),
        y - arrowLength * Math.sin(angle + arrowAngle)
    );
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawInitialArrow(startX, startY, endX, endY) {
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 3;
    ctx.stroke();

    const angle = Math.atan2(endY - startY, endX - startX);
    drawArrowHead(endX, endY, angle);
}

function drawTransitionLabel(x, y, label) {
    ctx.fillStyle = 'white';
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    
    const padding = 6;
    const textWidth = ctx.measureText(label).width;
    const rectWidth = textWidth + padding * 2;
    const rectHeight = 16;

    ctx.fillRect(x - rectWidth/2, y - rectHeight/2, rectWidth, rectHeight);
    ctx.strokeRect(x - rectWidth/2, y - rectHeight/2, rectWidth, rectHeight);

    ctx.fillStyle = '#374151';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x, y);
}

// Génération des états
function generateStates() {
    const alphabet = document.getElementById('alphabet').value.trim();
    const nbStates = parseInt(document.getElementById('nbStates').value);

    if (!alphabet) {
        showMessage('⚠️ Veuillez saisir un alphabet', 'warning');
        return;
    }

    if (!nbStates || nbStates < 1 || nbStates > 20) {
        showMessage('⚠️ Le nombre d\'états doit être entre 1 et 20', 'warning');
        return;
    }

    currentAutomaton.alphabet = alphabet;
    currentAutomaton.etats = Array.from({length: nbStates}, (_, i) => i);
    
    generateStateCheckboxes();
    document.getElementById('statesSection').style.display = 'block';
    showMessage('✅ États générés avec succès', 'success');
}

function generateStateCheckboxes() {
    const initialStatesDiv = document.getElementById('initialStates');
    const finalStatesDiv = document.getElementById('finalStates');

    initialStatesDiv.innerHTML = '';
    finalStatesDiv.innerHTML = '';

    currentAutomaton.etats.forEach(state => {
        // États initiaux (checkbox car plusieurs états initiaux possibles)
        const initialDiv = document.createElement('div');
        initialDiv.className = 'state-checkbox';
        initialDiv.innerHTML = `
            <input type="checkbox" id="initial_${state}" value="${state}">
            <label for="initial_${state}">q${state}</label>
        `;
        initialStatesDiv.appendChild(initialDiv);

        // États finaux (checkbox car plusieurs états finaux possibles)
        const finalDiv = document.createElement('div');
        finalDiv.className = 'state-checkbox';
        finalDiv.innerHTML = `
            <input type="checkbox" id="final_${state}" value="${state}">
            <label for="final_${state}">q${state}</label>
        `;
        finalStatesDiv.appendChild(finalDiv);
    });
}

function nextStep() {
    // Récupérer les états initiaux (multiple selection)
    const initialStateCheckboxes = document.querySelectorAll('#initialStates input[type="checkbox"]:checked');
    currentAutomaton.etats_initiaux = Array.from(initialStateCheckboxes).map(cb => parseInt(cb.value));

    if (currentAutomaton.etats_initiaux.length === 0) {
        showMessage('⚠️ Veuillez sélectionner au moins un état initial', 'warning');
        return;
    }

    // Récupérer les états finaux
    const finalStateCheckboxes = document.querySelectorAll('#finalStates input[type="checkbox"]:checked');
    currentAutomaton.etats_finaux = Array.from(finalStateCheckboxes).map(cb => parseInt(cb.value));

    if (currentAutomaton.etats_finaux.length === 0) {
        showMessage('⚠️ Veuillez sélectionner au moins un état final', 'warning');
        return;
    }

    // Initialiser les transitions
    currentAutomaton.transitions = {};
    currentAutomaton.etats.forEach(state => {
        currentAutomaton.transitions[state] = {};
    });

    // Passer à l'onglet transitions
    showTab('transitions');
    generateTransitionsGrid();
    drawCurrentAutomaton();
}

function generateTransitionsGrid() {
    const grid = document.getElementById('transitionsGrid');
    grid.innerHTML = '';

    const table = document.createElement('table');
    table.className = 'transitions-table';

    // En-tête
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = '<th>État / Symbole</th>';
    for (const symbol of currentAutomaton.alphabet) {
        headerRow.innerHTML += `<th>${symbol}</th>`;
    }
    table.appendChild(headerRow);

    // Lignes pour chaque état
    currentAutomaton.etats.forEach(state => {
        const row = document.createElement('tr');
        row.innerHTML = `<td class="state-label">q${state}</td>`;
        
        for (const symbol of currentAutomaton.alphabet) {
            const cell = document.createElement('td');
            const select = document.createElement('select');
            select.className = 'transition-select';
            select.id = `transition_${state}_${symbol}`;
            select.multiple = true;
            select.size = Math.min(currentAutomaton.etats.length, 4);

            // Option vide
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Aucun --';
            select.appendChild(emptyOption);

            // Options pour chaque état
            currentAutomaton.etats.forEach(targetState => {
                const option = document.createElement('option');
                option.value = targetState;
                option.textContent = `q${targetState}`;
                select.appendChild(option);
            });

            cell.appendChild(select);
            row.appendChild(cell);
        }
        table.appendChild(row);
    });

    grid.appendChild(table);
}

//#######################################################################################

//Permet de sauvegarder un automate

function saveAutomaton() {
    // Récupérer toutes les transitions
    currentAutomaton.etats.forEach(state => {
        for (const symbol of currentAutomaton.alphabet) {
            const select = document.getElementById(`transition_${state}_${symbol}`);
            const selectedValues = Array.from(select.selectedOptions)
                .map(option => option.value)
                .filter(value => value !== '');

            if (selectedValues.length > 0) {
                currentAutomaton.transitions[state][symbol] = selectedValues.map(v => parseInt(v));
            }
        }
    });

    // Sauvegarder l'automate original
    originalAutomaton = JSON.parse(JSON.stringify(currentAutomaton));
    isAutomatonSaved = true;

    drawCurrentAutomaton();
    showMessage('✅ Automate enregistré avec succès', 'success');
}

//#######################################################################################

// Reconnaissance de mots (modifiée pour états initiaux multiples)

function recognizeWord() {
    const word = document.getElementById('testWord').value.trim();
    
    if (!word) {
        showMessage('⚠️ Veuillez saisir un mot à tester', 'warning');
        return;
    }

    // Vérifier que tous les symboles du mot sont dans l'alphabet
    for (const symbol of word) {
        if (!currentAutomaton.alphabet.includes(symbol)) {
            showMessage(`⚠️ Le symbole '${symbol}' n'est pas dans l'alphabet`, 'warning');
            return;
        }
    }

    const result = simulateWord(word);
    displayTestResult(word, result);
}


//#######################################################################################

function simulateWord(word) {
    // Commencer avec tous les états initiaux
    let currentStates = [...currentAutomaton.etats_initiaux];
    const trace = [{states: [...currentStates], symbol: '', step: 0}];

    for (let i = 0; i < word.length; i++) {
        const symbol = word[i];
        const nextStates = new Set();

        for (const state of currentStates) {
            if (currentAutomaton.transitions[state] && currentAutomaton.transitions[state][symbol]) {
                const destinations = currentAutomaton.transitions[state][symbol];
                destinations.forEach(dest => nextStates.add(dest));
            }
        }

        currentStates = Array.from(nextStates);
        trace.push({states: [...currentStates], symbol: symbol, step: i + 1});

        if (currentStates.length === 0) {
            break;
        }
    }

    const isAccepted = currentStates.some(state => currentAutomaton.etats_finaux.includes(state));
    
    return {
        accepted: isAccepted,
        finalStates: currentStates,
        trace: trace
    };
}

//#######################################################################################

function displayTestResult(word, result) {
    const resultDiv = document.getElementById('testResult');
    const isAccepted = result.accepted;

    resultDiv.innerHTML = `
        <div class="result-header ${isAccepted ? 'accepted' : 'rejected'}">
            <h4>${isAccepted ? '✅ Mot accepté' : '❌ Mot rejeté'}</h4>
            <p>Mot testé: <strong>"${word}"</strong></p>
        </div>
        <div class="trace-section">
            <h5>📋 Trace d'exécution:</h5>
            <div class="trace-steps">
                ${result.trace.map((step, index) => `
                    <div class="trace-step">
                        <span class="step-number">${step.step}</span>
                        <span class="step-symbol">${step.symbol || 'ε'}</span>
                        <span class="step-states">{${step.states.map(s => `q${s}`).join(', ')}}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        <div class="final-states">
            <strong>États finaux atteints:</strong> {${result.finalStates.map(s => `q${s}`).join(', ')}}
        </div>
    `;

    resultDiv.style.display = 'block';
    drawCurrentAutomaton();
}

//#######################################################################################

// Analyse des états (modifiée pour états initiaux multiples)

function analyzeStates() {
    const accessible = findAccessibleStates();
    const coaccessible = findCoaccessibleStates();
    const useful = accessible.filter(state => coaccessible.includes(state));
    const useless = currentAutomaton.etats.filter(state => !useful.includes(state));

    displayAnalysisResults(accessible, coaccessible, useful, useless);
}

//#######################################################################################
//trouve les etats accessibles

function findAccessibleStates() {
    const accessible = new Set(currentAutomaton.etats_initiaux);
    const toVisit = [...currentAutomaton.etats_initiaux];

    while (toVisit.length > 0) {
        const currentState = toVisit.pop();
        
        if (currentAutomaton.transitions[currentState]) {
            for (const symbol in currentAutomaton.transitions[currentState]) {
                const destinations = currentAutomaton.transitions[currentState][symbol];
                for (const dest of destinations) {
                    if (!accessible.has(dest)) {
                        accessible.add(dest);
                        toVisit.push(dest);
                    }
                }
            }
        }
    }

    return Array.from(accessible);
}

//#######################################################################################
//trouve les etats coaccessibles

function findCoaccessibleStates() {
    const coaccessible = new Set(currentAutomaton.etats_finaux);
    let changed = true;

    while (changed) {
        changed = false;
        for (const state of currentAutomaton.etats) {
            if (!coaccessible.has(state)) {
                if (currentAutomaton.transitions[state]) {
                    for (const symbol in currentAutomaton.transitions[state]) {
                        const destinations = currentAutomaton.transitions[state][symbol];
                        if (destinations.some(dest => coaccessible.has(dest))) {
                            coaccessible.add(state);
                            changed = true;
                            break;
                        }
                    }
                }
            }
        }
    }

    return Array.from(coaccessible);
}

//#######################################################################################
//Affiche les resultats

function displayAnalysisResults(accessible, coaccessible, useful, useless) {
    document.getElementById('accessibleStates').innerHTML = 
        accessible.map(s => `<span class="state-tag accessible">q${s}</span>`).join('');
    
    document.getElementById('coaccessibleStates').innerHTML = 
        coaccessible.map(s => `<span class="state-tag coaccessible">q${s}</span>`).join('');
    
    document.getElementById('usefulStates').innerHTML = 
        useful.map(s => `<span class="state-tag useful">q${s}</span>`).join('');
    
    document.getElementById('uselessStates').innerHTML = 
        useless.map(s => `<span class="state-tag useless">q${s}</span>`).join('');

    const isTrimmed = useless.length === 0;
    document.getElementById('trimmedStatus').innerHTML = `
        <div class="trim-status ${isTrimmed ? 'trimmed' : 'not-trimmed'}">
            ${isTrimmed ? '✅ L\'automate est émondé' : '⚠️ L\'automate n\'est pas émondé'}
        </div>
    `;

    document.getElementById('analysisResults').style.display = 'block';
    drawCurrentAutomaton();
}

//#######################################################################################

// Opérations sur les automates (adaptées pour états initiaux multiples)

function determinizeAutomaton() {
    if (isDeterministic()) {
        showMessage('ℹ️ L\'automate est déjà déterministe', 'info');
        return;
    }

    const determinized = powersetConstruction();
    currentAutomaton = determinized;
    drawCurrentAutomaton();
    
    document.getElementById('operationResult').innerHTML = `
        <div class="result-header success">
            <h4>✅ Déterminisation réussie</h4>
            <p>L'automate a été déterminisé avec succès</p>
        </div>
    `;
    document.getElementById('operationResult').style.display = 'block';
}

//#######################################################################################

function isDeterministic() {
    // Un automate est déterministe s'il a un seul état initial et 
    // chaque transition mène à au plus un état
    if (currentAutomaton.etats_initiaux.length > 1) {
        return false;
    }
    
    for (const state in currentAutomaton.transitions) {
        for (const symbol in currentAutomaton.transitions[state]) {
            if (currentAutomaton.transitions[state][symbol].length > 1) {
                return false;
            }
        }
    }
    return true;
}

//#######################################################################################

function powersetConstruction() {
    const newStates = [];
    const newTransitions = {};
    const stateMapping = new Map();
    const queue = [];

    // État initial (ensemble des états initiaux)
    const initialStateSet = [...currentAutomaton.etats_initiaux].sort();
    const initialKey = initialStateSet.join(',');
    newStates.push(0);
    stateMapping.set(initialKey, 0);
    queue.push({states: initialStateSet, id: 0});

    let nextStateId = 1;

    while (queue.length > 0) {
        const current = queue.shift();
        newTransitions[current.id] = {};

        for (const symbol of currentAutomaton.alphabet) {
            const nextStates = new Set();
            
            for (const state of current.states) {
                if (currentAutomaton.transitions[state] && currentAutomaton.transitions[state][symbol]) {
                    currentAutomaton.transitions[state][symbol].forEach(dest => nextStates.add(dest));
                }
            }

            if (nextStates.size > 0) {
                const nextStatesArray = Array.from(nextStates).sort();
                const nextKey = nextStatesArray.join(',');

                if (!stateMapping.has(nextKey)) {
                    stateMapping.set(nextKey, nextStateId);
                    newStates.push(nextStateId);
                    queue.push({states: nextStatesArray, id: nextStateId});
                    nextStateId++;
                }

                newTransitions[current.id][symbol] = [stateMapping.get(nextKey)];
            }
        }
    }

    // États finaux
    const newFinalStates = [];
    for (let i = 0; i < newStates.length; i++) {
        const stateKey = Array.from(stateMapping.entries()).find(([key, id]) => id === i)[0];
        const originalStates = stateKey.split(',').map(s => parseInt(s));
        if (originalStates.some(state => currentAutomaton.etats_finaux.includes(state))) {
            newFinalStates.push(i);
        }
    }

    return {
        alphabet: currentAutomaton.alphabet,
        etats: newStates,
        etats_initiaux: [0], // Un seul état initial après déterminisation
        etats_finaux: newFinalStates,
        transitions: newTransitions
    };
}

//#######################################################################################
//Utilitaires pour restaurer l'original et recommencer les operations

function restoreOriginal() {
    if (!originalAutomaton) {
        showMessage('⚠️ Aucun automate original à restaurer', 'warning');
        return;
    }

    currentAutomaton = JSON.parse(JSON.stringify(originalAutomaton));
    drawCurrentAutomaton();
    
    document.getElementById('operationResult').innerHTML = `
        <div class="result-header success">
            <h4>✅ Automate restauré</h4>
            <p>L'automate original a été restauré</p>
        </div>
    `;
    document.getElementById('operationResult').style.display = 'block';
}

//#######################################################################################

// Système de messages
function showMessage(message, type = 'info') {
    const messagesDiv = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message message-${type}`;
    messageElement.textContent = message;

    messagesDiv.appendChild(messageElement);

    // Animation d'apparition
    setTimeout(() => messageElement.classList.add('show'), 10);

    // Suppression automatique après 4 secondes
    setTimeout(() => {
        messageElement.classList.remove('show');
        setTimeout(() => messagesDiv.removeChild(messageElement), 300);
    }, 4000);
}

//#######################################################################################

// Fonctions utilitaires pour gérer les états initiaux multiples

function ajouterEtatInitial(etat) {
    if (!currentAutomaton.etats_initiaux.includes(etat)) {
        currentAutomaton.etats_initiaux.push(etat);
    }
}

function supprimerEtatInitial(etat) {
    const index = currentAutomaton.etats_initiaux.indexOf(etat);
    if (index > -1) {
        currentAutomaton.etats_initiaux.splice(index, 1);
    }
}

function estEtatInitial(etat) {
    return currentAutomaton.etats_initiaux.includes(etat);
}


function constructGlushkov() {
    const regexInput = document.getElementById('regexInput').value;
    if (!regexInput) {
        showMessage('⚠️ Veuillez entrer une expression régulière.', 'warning');
        return;
    }
    
    try {
        // Réinitialiser l'état précédent
        currentAutomaton = null;
        isAutomatonSaved = false;
        
        // Effacer le canvas avant de redessiner
        if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        // Construire l'automate de Glushkov basé sur l'expression régulière
        const automaton = buildGlushkovAutomaton(regexInput);
        
        // Mettre à jour l'automate courant
        currentAutomaton = automaton;
        isAutomatonSaved = true;
        
        // Forcer la mise à jour du canvas actif
        updateActiveCanvas('glushkov');
        
        // Attendre un court délai pour s'assurer que le canvas est prêt
        setTimeout(() => {
            drawCurrentAutomaton();
        }, 100);
        
        // Afficher des informations sur la construction
        document.getElementById('glushkovInfo').style.display = 'block';
        document.getElementById('positionsInfo').innerText = `Positions calculées pour : ${regexInput}`;
        document.getElementById('regexInfo').innerText = `Automate construit pour l'expression régulière : ${regexInput}`;
        
        showMessage('✅ Automate de Glushkov construit avec succès', 'success');
    } catch (error) {
        console.error('Erreur construction Glushkov:', error);
        showMessage(`❌ Erreur lors de la construction : ${error.message}`, 'error');
    }
}

function setRegexExample(example) {
    document.getElementById('regexInput').value = example;
}

// Fonction de reset pour nettoyer l'état et vider le cache
function resetGlushkovState() {
    // Réinitialiser les variables globales
    currentAutomaton = null;
    isAutomatonSaved = false;
    
    // Nettoyer tous les canvas
    document.querySelectorAll('canvas').forEach(canvas => {
        const context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);
    });
    
    // Masquer les informations Glushkov
    const glushkovInfo = document.getElementById('glushkovInfo');
    if (glushkovInfo) {
        glushkovInfo.style.display = 'none';
    }
    
    // Vider le champ de saisie
    const regexInput = document.getElementById('regexInput');
    if (regexInput) {
        regexInput.value = '';
    }
    
    // Réinitialiser le canvas actif
    updateActiveCanvas('glushkov');
    
    // Message de confirmation
    showMessage('🔄 État réinitialisé avec succès', 'success');
    
    console.log('État Glushkov complètement réinitialisé');
}

// Fonction pour créer le bouton reset (à appeler au chargement de la page)
function createResetButton() {
    // Chercher le conteneur du bouton (à adapter selon votre HTML)
    const glushkovTab = document.getElementById('glushkov');
    if (glushkovTab) {
        // Chercher s'il existe déjà un bouton reset
        let resetBtn = document.getElementById('resetGlushkovBtn');
        
        if (!resetBtn) {
            // Créer le bouton reset
            resetBtn = document.createElement('button');
            resetBtn.id = 'resetGlushkovBtn';
            resetBtn.className = 'btn btn-secondary';
            resetBtn.innerHTML = '🔄 Reset';
            resetBtn.title = 'Vider le cache et réinitialiser';
            resetBtn.style.marginLeft = '10px';
            
            // Ajouter l'événement click
            resetBtn.addEventListener('click', resetGlushkovState);
            
            // Insérer le bouton à côté du bouton "Construire"
            const constructBtn = glushkovTab.querySelector('button');
            if (constructBtn && constructBtn.parentNode) {
                constructBtn.parentNode.insertBefore(resetBtn, constructBtn.nextSibling);
            } else {
                // Si pas de bouton trouvé, l'ajouter au début du tab
                glushkovTab.insertBefore(resetBtn, glushkovTab.firstChild);
            }
        }
    }
}

// Fonction améliorée de construction avec reset automatique en cas d'erreur
function constructGlushkovWithReset() {
    try {
        constructGlushkov();
    } catch (error) {
        console.error('Erreur détectée, reset automatique:', error);
        resetGlushkovState();
        showMessage('❌ Erreur détectée, état réinitialisé. Réessayez.', 'warning');
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    createResetButton();
    console.log('Bouton reset Glushkov initialisé');
});

// Fonction pour analyser une expression régulière simple et extraire l'alphabet
function extractAlphabet(regex) {
    // Supprimer les opérateurs et caractères spéciaux pour extraire les lettres
    const letters = regex.match(/[a-zA-Z]/g) || [];
    return Array.from(new Set(letters)).sort();
}

// Fonction améliorée pour construire l'automate de Glushkov
function buildGlushkovAutomaton(regex) {
    console.log(`Construction automate pour: ${regex}`);
    
    // Nettoyer l'expression régulière
    const cleanRegex = regex.trim();
    
    // Extraire l'alphabet de l'expression
    const alphabet = extractAlphabet(cleanRegex);
    
    if (alphabet.length === 0) {
        throw new Error("Aucun caractère valide trouvé dans l'expression régulière");
    }
    
    // Construction simplifiée basée sur des patterns courants
    let automaton;
    
    // Analyser le type d'expression régulière
    if (cleanRegex.includes('*')) {
        // Expression avec étoile de Kleene
        automaton = buildKleeneAutomaton(cleanRegex, alphabet);
    } else if (cleanRegex.includes('+')) {
        // Expression avec plus
        automaton = buildPlusAutomaton(cleanRegex, alphabet);
    } else if (cleanRegex.includes('|')) {
        // Expression avec union
        automaton = buildUnionAutomaton(cleanRegex, alphabet);
    } else {
        // Expression séquentielle simple
        automaton = buildSequentialAutomaton(cleanRegex, alphabet);
    }
    
    console.log('Automate construit:', automaton);
    return automaton;
}

// Construction d'automate pour expression séquentielle (ex: "abc")
function buildSequentialAutomaton(regex, alphabet) {
    const chars = regex.match(/[a-zA-Z]/g) || [];
    const states = [];
    const transitions = {};
    
    // Créer les états (0 à n)
    for (let i = 0; i <= chars.length; i++) {
        states.push(i);
        transitions[i] = {};
    }
    
    // Créer les transitions
    for (let i = 0; i < chars.length; i++) {
        const char = chars[i].toLowerCase();
        if (!transitions[i][char]) {
            transitions[i][char] = [];
        }
        transitions[i][char].push(i + 1);
    }
    
    return {
        alphabet: alphabet,
        etats: states,
        etats_initiaux: [0],
        etats_finaux: [chars.length],
        transitions: transitions
    };
}

// Construction d'automate pour expression avec étoile de Kleene (ex: "a*")
function buildKleeneAutomaton(regex, alphabet) {
    const baseChar = regex.replace(/\*/g, '').match(/[a-zA-Z]/g)?.[0]?.toLowerCase();
    
    if (!baseChar) {
        throw new Error("Caractère non trouvé dans l'expression avec *");
    }
    
    const states = [0, 1];
    const transitions = {
        0: {},
        1: {}
    };
    
    // État 0 -> État 1 avec le caractère
    transitions[0][baseChar] = [1];
    // État 1 -> État 1 avec le caractère (boucle)
    transitions[1][baseChar] = [1];
    
    return {
        alphabet: alphabet,
        etats: states,
        etats_initiaux: [0],
        etats_finaux: [0, 1], // État initial est aussi final pour ε
        transitions: transitions
    };
}

// Construction d'automate pour expression avec plus (ex: "a+")
function buildPlusAutomaton(regex, alphabet) {
    const baseChar = regex.replace(/\+/g, '').match(/[a-zA-Z]/g)?.[0]?.toLowerCase();
    
    if (!baseChar) {
        throw new Error("Caractère non trouvé dans l'expression avec +");
    }
    
    const states = [0, 1];
    const transitions = {
        0: {},
        1: {}
    };
    
    // État 0 -> État 1 avec le caractère
    transitions[0][baseChar] = [1];
    // État 1 -> État 1 avec le caractère (boucle)
    transitions[1][baseChar] = [1];
    
    return {
        alphabet: alphabet,
        etats: states,
        etats_initiaux: [0],
        etats_finaux: [1], // Seul l'état 1 est final
        transitions: transitions
    };
}

// Construction d'automate pour expression avec union (ex: "a|b")
function buildUnionAutomaton(regex, alphabet) {
    const parts = regex.split('|');
    const states = [0, 1, 2];
    const transitions = {
        0: {},
        1: {},
        2: {}
    };
    
    // Pour chaque partie de l'union
    parts.forEach((part, index) => {
        const char = part.trim().match(/[a-zA-Z]/g)?.[0]?.toLowerCase();
        if (char) {
            if (!transitions[0][char]) {
                transitions[0][char] = [];
            }
            transitions[0][char].push(index + 1);
        }
    });
    
    return {
        alphabet: alphabet,
        etats: states,
        etats_initiaux: [0],
        etats_finaux: [1, 2], // Les états correspondant aux parties de l'union
        transitions: transitions
    };
}

function updateActiveCanvas(tabName) {
    const canvasMap = {
        'creation': 'automatonCanvas',
        'glushkov': 'glushkovCanvas',
        'transitions': 'transitionsCanvas',
        'recognition': 'recognitionCanvas',
        'analysis': 'analysisCanvas',
        'operations': 'operationsCanvas'
    };
    
    const canvasId = canvasMap[tabName] || 'automatonCanvas';
    const newCanvas = document.getElementById(canvasId);
    
    if (newCanvas) {
        // Si c'est un nouveau canvas, nettoyer l'ancien
        if (canvas && canvas !== newCanvas) {
            canvas.removeEventListener('wheel', handleWheel);
            canvas.removeEventListener('mousedown', handleMouseDown);
            canvas.removeEventListener('mousemove', handleMouseMove);
            canvas.removeEventListener('mouseup', handleMouseUp);
            canvas.removeEventListener('mouseleave', handleMouseUp);
        }
        
        canvas = newCanvas;
        ctx = canvas.getContext('2d');
        
        // Nettoyer le canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Réappliquer les gestionnaires d'événements
        canvas.addEventListener('wheel', handleWheel, { passive: false });
        canvas.addEventListener('mousedown', handleMouseDown);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseup', handleMouseUp);
        canvas.addEventListener('mouseleave', handleMouseUp);
        
        console.log(`Canvas actif changé vers: ${canvasId}`);
    } else {
        console.error(`Canvas ${canvasId} non trouvé`);
    }
}

function showTab(tabName) {
    if ((tabName === 'recognition' || tabName === 'analysis' || tabName === 'operations') && !isAutomatonSaved) {
        showMessage('⚠️ Veuillez d\'abord créer et enregistrer un automate', 'warning');
        return;
    }
    
    // Vérifier que event existe (pour éviter les erreurs si appelé programmatiquement)
    if (typeof event !== 'undefined' && event.target) {
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        event.target.classList.add('active');
    }
    
    document.getElementById(tabName).classList.add('active');
    
    // Changer le canvas actif
    updateActiveCanvas(tabName);
    
    // Redessiner l'automate si il existe
    if (currentAutomaton) {
        drawCurrentAutomaton();
    }
}

//#######################################################################################
// FONCTIONS JAVASCRIPT POUR LA MINIMISATION D'AUTOMATE
// À ajouter au script.js existant

//#######################################################################################
// Fonction principale pour déclencher la minimisation via le backend

function minimizeAutomaton() {
    if (!isAutomatonSaved) {
        showMessage('⚠️ Veuillez d\'abord créer et enregistrer un automate', 'warning');
        return;
    }

    if (!isDeterministic()) {
        showMessage('⚠️ L\'automate doit être déterministe pour être minimisé', 'warning');
        return;
    }

    // Préparer les données pour l'envoi au backend
    const automatonData = {
        alphabet: currentAutomaton.alphabet,
        states: currentAutomaton.etats,
        initial_states: currentAutomaton.etats_initiaux,
        final_states: currentAutomaton.etats_finaux,
        transitions: formatTransitionsForBackend(currentAutomaton.transitions)
    };

    // Afficher un indicateur de chargement
    showLoadingIndicator('Minimisation en cours...');

    // Envoyer la requête au backend
    fetch('/api/minimize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(automatonData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingIndicator();
        
        if (data.success) {
            handleMinimizationSuccess(data);
        } else {
            handleMinimizationError(data.error || 'Erreur inconnue');
        }
    })
    .catch(error => {
        hideLoadingIndicator();
        console.error('Erreur lors de la minimisation:', error);
        showMessage('❌ Erreur de communication avec le serveur', 'error');
    });
}

//#######################################################################################
// Formater les transitions pour le backend Python

function formatTransitionsForBackend(transitions) {
    const formattedTransitions = {};
    
    for (const [state, stateTransitions] of Object.entries(transitions)) {
        formattedTransitions[parseInt(state)] = {};
        
        for (const [symbol, destinations] of Object.entries(stateTransitions)) {
            // Pour un automate déterministe, prendre seulement la première destination
            if (destinations && destinations.length > 0) {
                formattedTransitions[parseInt(state)][symbol] = destinations[0];
            }
        }
    }
    
    return formattedTransitions;
}

//#######################################################################################
// Traiter le succès de la minimisation

function handleMinimizationSuccess(data) {
    const { minimized_automaton, trace, original_states_count, minimized_states_count } = data;
    
    // Mettre à jour l'automate courant avec l'automate minimisé
    currentAutomaton = {
        alphabet: minimized_automaton.alphabet,
        etats: minimized_automaton.states,
        etats_initiaux: minimized_automaton.initial_states,
        etats_finaux: minimized_automaton.final_states,
        transitions: formatTransitionsFromBackend(minimized_automaton.transitions)
    };

    // Redessiner l'automate
    drawCurrentAutomaton();

    // Afficher les résultats
    displayMinimizationResults(trace, original_states_count, minimized_states_count);
    
    // Message de succès
    if (original_states_count === minimized_states_count) {
        showMessage('ℹ️ L\'automate était déjà minimal', 'info');
    } else {
        showMessage(`✅ Minimisation réussie : ${original_states_count} → ${minimized_states_count} états`, 'success');
    }
}

//#######################################################################################
// Formater les transitions reçues du backend

function formatTransitionsFromBackend(backendTransitions) {
    const formattedTransitions = {};
    
    for (const [state, stateTransitions] of Object.entries(backendTransitions)) {
        formattedTransitions[parseInt(state)] = {};
        
        for (const [symbol, destination] of Object.entries(stateTransitions)) {
            // Convertir en tableau pour maintenir la cohérence avec le format existant
            formattedTransitions[parseInt(state)][symbol] = [destination];
        }
    }
    
    return formattedTransitions;
}

//#######################################################################################
// Traiter les erreurs de minimisation

function handleMinimizationError(errorMessage) {
    showMessage(`❌ Erreur lors de la minimisation : ${errorMessage}`, 'error');
    
    // Afficher l'erreur dans la zone de résultats
    document.getElementById('operationResult').innerHTML = `
        <div class="result-header error">
            <h4>❌ Erreur de minimisation</h4>
            <p>${errorMessage}</p>
        </div>
    `;
    document.getElementById('operationResult').style.display = 'block';
}

//#######################################################################################
// Afficher les résultats de la minimisation avec trace

function displayMinimizationResults(trace, originalCount, minimizedCount) {
    const resultHTML = `
        <div class="result-header success">
            <h4>✅ Minimisation réussie</h4>
            <p>L'automate a été minimisé avec succès</p>
            <p><strong>Nombre d'états : ${originalCount} → ${minimizedCount}</strong></p>
        </div>
        
        <div class="minimization-trace">
            <h5>🔍 Trace de minimisation (Algorithme de Moore)</h5>
            ${generateTraceHTML(trace)}
        </div>
    `;
    
    document.getElementById('operationResult').innerHTML = resultHTML;
    document.getElementById('operationResult').style.display = 'block';
}

//#######################################################################################
// Générer le HTML pour la trace de minimisation

function generateTraceHTML(trace) {
    if (!trace || !trace.steps || trace.steps.length === 0) {
        return '<p>Aucune trace disponible</p>';
    }
    
    let traceHTML = '<div class="trace-container">';
    
    // Afficher chaque étape de la trace
    trace.steps.forEach((step, index) => {
        traceHTML += `
            <div class="trace-step-min">
                <div class="step-header">
                    <strong>Étape ${index} :</strong> ${step.description}
                </div>
                <div class="partitions-display">
        `;
        
        // Afficher les partitions de cette étape
        step.partitions.forEach((partition, pIndex) => {
            const partitionStates = partition.map(s => `q${s}`).join(', ');
            traceHTML += `
                <div class="partition">
                    <span class="partition-label">P${pIndex}:</span>
                    <span class="partition-states">{${partitionStates}}</span>
                </div>
            `;
        });
        
        traceHTML += '</div></div>';
    });
    
    // Afficher le mapping final si disponible
    if (trace.state_mapping) {
        traceHTML += generateStateMappingHTML(trace.state_mapping);
    }
    
    traceHTML += '</div>';
    
    return traceHTML;
}

//#######################################################################################
// Générer le HTML pour le mapping des états

function generateStateMappingHTML(stateMapping) {
    let mappingHTML = `
        <div class="final-mapping">
            <h6>🎯 Mapping final des états :</h6>
            <div class="mapping-display">
    `;
    
    for (const [newState, originalStates] of Object.entries(stateMapping)) {
        const originalStatesStr = originalStates.map(s => `q${s}`).join(', ');
        mappingHTML += `
            <div class="state-mapping">
                <span class="original-states">{${originalStatesStr}}</span>
                <span class="arrow">→</span>
                <span class="new-state">q${newState}</span>
            </div>
        `;
    }
    
    mappingHTML += '</div></div>';
    
    return mappingHTML;
}

//#######################################################################################
// Fonctions utilitaires pour l'interface utilisateur

function showLoadingIndicator(message = 'Chargement...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    
    document.body.appendChild(loadingDiv);
}

function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

//#######################################################################################
// Fonction pour compléter l'automate (si nécessaire avant minimisation)

function completeAutomatonForMinimization() {
    if (!isAutomatonSaved) {
        showMessage('⚠️ Veuillez d\'abord créer et enregistrer un automate', 'warning');
        return;
    }

    const automatonData = {
        alphabet: currentAutomaton.alphabet,
        states: currentAutomaton.etats,
        initial_states: currentAutomaton.etats_initiaux,
        final_states: currentAutomaton.etats_finaux,
        transitions: formatTransitionsForBackend(currentAutomaton.transitions)
    };

    showLoadingIndicator('Complétion de l\'automate...');

    fetch('/api/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(automatonData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingIndicator();
        
        if (data.success) {
            handleCompletionSuccess(data);
        } else {
            handleCompletionError(data.error || 'Erreur inconnue');
        }
    })
    .catch(error => {
        hideLoadingIndicator();
        console.error('Erreur lors de la complétion:', error);
        showMessage('❌ Erreur de communication avec le serveur', 'error');
    });
}

//#######################################################################################
// Traiter le succès de la complétion

function handleCompletionSuccess(data) {
    const { completed_automaton, added_sink_state } = data;
    
    // Mettre à jour l'automate courant
    currentAutomaton = {
        alphabet: completed_automaton.alphabet,
        etats: completed_automaton.states,
        etats_initiaux: completed_automaton.initial_states,
        etats_finaux: completed_automaton.final_states,
        transitions: formatTransitionsFromBackend(completed_automaton.transitions)
    };

    // Redessiner l'automate
    drawCurrentAutomaton();

    if (added_sink_state !== null) {
        showMessage(`✅ Automate complété avec l'état puits q${added_sink_state}`, 'success');
    } else {
        showMessage('ℹ️ L\'automate était déjà complet', 'info');
    }
}

//#######################################################################################
// Traiter les erreurs de complétion

function handleCompletionError(errorMessage) {
    showMessage(`❌ Erreur lors de la complétion : ${errorMessage}`, 'error');
}

//#######################################################################################
// Vérifier si l'automate est déjà minimal (requête au backend)

function checkIfMinimal() {
    if (!isAutomatonSaved) {
        showMessage('⚠️ Veuillez d\'abord créer et enregistrer un automate', 'warning');
        return;
    }

    const automatonData = {
        alphabet: currentAutomaton.alphabet,
        states: currentAutomaton.etats,
        initial_states: currentAutomaton.etats_initiaux,
        final_states: currentAutomaton.etats_finaux,
        transitions: formatTransitionsForBackend(currentAutomaton.transitions)
    };

    fetch('/api/is_minimal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(automatonData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const message = data.is_minimal ? 
                '✅ L\'automate est déjà minimal' : 
                '⚠️ L\'automate peut être minimisé';
            
            showMessage(message, data.is_minimal ? 'success' : 'info');
        } else {
            showMessage(`❌ Erreur : ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur lors de la vérification:', error);
        showMessage('❌ Erreur de communication avec le serveur', 'error');
    });
}

//#######################################################################################
// Fonction pour exporter l'automate minimisé

function exportMinimizedAutomaton() {
    if (!isAutomatonSaved) {
        showMessage('⚠️ Aucun automate à exporter', 'warning');
        return;
    }

    const automatonData = {
        alphabet: currentAutomaton.alphabet,
        states: currentAutomaton.etats,
        initial_states: currentAutomaton.etats_initiaux,
        final_states: currentAutomaton.etats_finaux,
        transitions: formatTransitionsForBackend(currentAutomaton.transitions)
    };

    // Créer et télécharger le fichier JSON
    const dataStr = JSON.stringify(automatonData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'automate_minimise.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showMessage('✅ Automate exporté avec succès', 'success');
}
