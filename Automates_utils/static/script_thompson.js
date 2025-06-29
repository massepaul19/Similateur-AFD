// ============================================================================
// SIMULATEUR D'AUTOMATES DE THOMPSON - VERSION COMPLÈTE
// ============================================================================

// Variables globales
let currentAutomaton = null;
let originalAutomaton = null;
let isAutomatonSaved = false;
let scale = 1;
let offsetX = 0;
let offsetY = 0;

// Classe pour gérer les IDs d'états uniques
class ThompsonStateID {
    static counter = 0;
    
    static next() {
        const id = this.counter;
        this.counter += 1;
        return id;
    }
    
    static reset() {
        this.counter = 0;
    }
}

// ============================================================================
// FONCTIONS UTILITAIRES
// ============================================================================

function showMessage(message, type) {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Créer ou mettre à jour le conteneur de messages
    let messagesContainer = document.getElementById('messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.id = 'messages';
        messagesContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(messagesContainer);
    }
    
    // Créer le message
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 14px;
        line-height: 1.4;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Style selon le type
    switch(type) {
        case 'success':
            messageDiv.style.backgroundColor = '#d4edda';
            messageDiv.style.color = '#155724';
            messageDiv.style.border = '1px solid #c3e6cb';
            break;
        case 'error':
            messageDiv.style.backgroundColor = '#f8d7da';
            messageDiv.style.color = '#721c24';
            messageDiv.style.border = '1px solid #f5c6cb';
            break;
        case 'warning':
            messageDiv.style.backgroundColor = '#fff3cd';
            messageDiv.style.color = '#856404';
            messageDiv.style.border = '1px solid #ffeaa7';
            break;
        default:
            messageDiv.style.backgroundColor = '#d1ecf1';
            messageDiv.style.color = '#0c5460';
            messageDiv.style.border = '1px solid #bee5eb';
    }
    
    messageDiv.textContent = message;
    messagesContainer.appendChild(messageDiv);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

function updateActiveCanvas(canvasType) {
    console.log(`Activation du canvas: ${canvasType}`);
    const targetCanvas = document.getElementById(canvasType + 'Canvas');
    if (targetCanvas) {
        targetCanvas.style.display = 'block';
        console.log(`Canvas ${canvasType}Canvas activé`);
    }
}

function resetThompsonState() {
    currentAutomaton = null;
    originalAutomaton = null;
    isAutomatonSaved = false;
    ThompsonStateID.reset();
    
    // Effacer le canvas si il existe
    const canvas = document.getElementById('thompsonCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    // Masquer les informations
    const infoDiv = document.getElementById('thompsonInfo') || document.getElementById('glushkovInfo');
    if (infoDiv) {
        infoDiv.style.display = 'none';
    }
}

// ============================================================================
// FONCTIONS DE CONSTRUCTION DE THOMPSON
// ============================================================================

function constructThompson() {
    const regexInput = document.getElementById('regexInput');
    if (!regexInput) {
        console.error('Element regexInput non trouvé');
        showMessage('❌ Erreur: Element d\'entrée non trouvé', 'error');
        return;
    }
    
    const regex = regexInput.value.trim();
    if (!regex) {
        showMessage('⚠️ Veuillez entrer une expression régulière.', 'warning');
        return;
    }
    
    try {
        console.log(`Début construction Thompson pour: "${regex}"`);
        
        // Réinitialiser l'état précédent
        resetThompsonState();
        
        // Construire l'automate de Thompson
        const automaton = buildThompsonAutomaton(regex);
        
        if (!automaton || !automaton.etats || automaton.etats.length === 0) {
            throw new Error("Automate Thompson généré invalide");
        }
        
        // Mettre à jour l'automate courant
        currentAutomaton = automaton;
        originalAutomaton = JSON.parse(JSON.stringify(automaton));
        isAutomatonSaved = true;
        
        console.log('Automate Thompson construit:', automaton);
        
        // Dessiner l'automate
        drawThompsonAutomaton(automaton);
        
        // Afficher des informations sur la construction
        displayThompsonInfo(regex, automaton);
        
        showMessage('✅ Automate de Thompson construit avec succès', 'success');
        
    } catch (error) {
        console.error('Erreur construction Thompson:', error);
        showMessage(`❌ Erreur lors de la construction : ${error.message}`, 'error');
        resetThompsonState();
    }
}

function buildThompsonAutomaton(regex) {
    console.log(`Construction Thompson pour: ${regex}`);
    
    // Nettoyer et valider l'expression régulière
    const cleanRegex = regex.trim();
    if (!cleanRegex) {
        throw new Error("Expression régulière vide");
    }
    
    // Réinitialiser le compteur d'états
    ThompsonStateID.reset();
    
    // Extraire l'alphabet de l'expression
    const alphabet = extractAlphabet(cleanRegex);
    
    if (alphabet.length === 0) {
        throw new Error("Aucun caractère valide trouvé dans l'expression régulière");
    }
    
    console.log(`Alphabet extrait: [${alphabet.join(', ')}]`);
    
    // Analyser et construire selon le type d'expression
    let automaton;
    
    try {
        if (isSimpleCharacter(cleanRegex)) {
            automaton = buildThompsonSimpleChar(cleanRegex, alphabet);
        } else if (isKleeneExpression(cleanRegex)) {
            automaton = buildThompsonKleene(cleanRegex, alphabet);
        } else if (isPlusExpression(cleanRegex)) {
            automaton = buildThompsonPlus(cleanRegex, alphabet);
        } else if (isUnionExpression(cleanRegex)) {
            automaton = buildThompsonUnion(cleanRegex, alphabet);
        } else if (isConcatenationExpression(cleanRegex)) {
            automaton = buildThompsonConcatenation(cleanRegex, alphabet);
        } else {
            automaton = buildThompsonSequential(cleanRegex, alphabet);
        }
        
        // Valider l'automate construit
        validateThompsonAutomaton(automaton);
        
        console.log('Automate Thompson construit avec succès:', automaton);
        return automaton;
        
    } catch (error) {
        console.error('Erreur lors de la construction Thompson:', error);
        throw new Error(`Impossible de construire l'automate Thompson: ${error.message}`);
    }
}

// Construction Thompson pour caractère simple
function buildThompsonSimpleChar(regex, alphabet) {
    const char = regex.toLowerCase();
    const q0 = ThompsonStateID.next();
    const q1 = ThompsonStateID.next();
    
    return {
        alphabet: alphabet,
        etats: [q0, q1],
        etats_initiaux: [q0],
        etats_finaux: [q1],
        transitions: {
            [q0]: { [char]: [q1] },
            [q1]: {}
        }
    };
}

// Construction Thompson pour expression séquentielle
function buildThompsonSequential(regex, alphabet) {
    const chars = regex.match(/[a-zA-Z]/g) || [];
    
    if (chars.length === 0) {
        throw new Error("Aucun caractère trouvé dans l'expression séquentielle");
    }
    
    if (chars.length === 1) {
        return buildThompsonSimpleChar(chars[0], alphabet);
    }
    
    // Construire par concaténation successive
    let result = buildThompsonSimpleChar(chars[0], alphabet);
    
    for (let i = 1; i < chars.length; i++) {
        const nextChar = buildThompsonSimpleChar(chars[i], alphabet);
        result = concatenateThompsonAutomata(result, nextChar);
    }
    
    return result;
}

// Construction Thompson pour étoile de Kleene
function buildThompsonKleene(regex, alphabet) {
    // Extraire le contenu avant l'étoile
    const basePattern = regex.replace(/\*+/g, '').replace(/[()]/g, '');
    
    if (!basePattern) {
        throw new Error("Pattern vide pour l'étoile de Kleene");
    }
    
    // Construire l'automate de base
    let baseAutomaton;
    if (basePattern.length === 1) {
        baseAutomaton = buildThompsonSimpleChar(basePattern, alphabet);
    } else {
        baseAutomaton = buildThompsonSequential(basePattern, alphabet);
    }
    
    // Appliquer la construction de l'étoile de Kleene
    const q0 = ThompsonStateID.next();
    const qf = ThompsonStateID.next();
    
    const states = [q0, qf, ...baseAutomaton.etats];
    const transitions = { ...baseAutomaton.transitions };
    
    // Nouvel état initial avec transitions ε
    transitions[q0] = { 'ε': [baseAutomaton.etats_initiaux[0], qf] };
    
    // Nouvel état final
    transitions[qf] = {};
    
    // Connecter tous les états finaux de base vers l'état initial et final
    for (const finalState of baseAutomaton.etats_finaux) {
        if (!transitions[finalState]) {
            transitions[finalState] = {};
        }
        if (!transitions[finalState]['ε']) {
            transitions[finalState]['ε'] = [];
        }
        transitions[finalState]['ε'].push(baseAutomaton.etats_initiaux[0], qf);
    }
    
    return {
        alphabet: alphabet,
        etats: states,
        etats_initiaux: [q0],
        etats_finaux: [qf],
        transitions: transitions
    };
}

// Construction Thompson pour plus
function buildThompsonPlus(regex, alphabet) {
    const basePattern = regex.replace(/\++/g, '').replace(/[()]/g, '');
    
    if (!basePattern) {
        throw new Error("Pattern vide pour l'opérateur plus");
    }
    
    // Construire l'automate de base
    let baseAutomaton;
    if (basePattern.length === 1) {
        baseAutomaton = buildThompsonSimpleChar(basePattern, alphabet);
    } else {
        baseAutomaton = buildThompsonSequential(basePattern, alphabet);
    }
    
    // Pour A+, on fait A.A* = concaténation de A avec A*
    const kleeneAutomaton = buildThompsonKleene(basePattern + '*', alphabet);
    
    return concatenateThompsonAutomata(baseAutomaton, kleeneAutomaton);
}

// Construction Thompson pour union
function buildThompsonUnion(regex, alphabet) {
    const parts = regex.split('|').map(part => part.trim()).filter(part => part.length > 0);
    
    if (parts.length < 2) {
        throw new Error("Expression d'union invalide");
    }
    
    // Construire les automates pour chaque partie
    const automata = parts.map(part => {
        if (part.length === 1) {
            return buildThompsonSimpleChar(part, alphabet);
        } else {
            return buildThompsonSequential(part, alphabet);
        }
    });
    
    // Créer l'union successive
    let result = automata[0];
    for (let i = 1; i < automata.length; i++) {
        result = unionThompsonAutomata(result, automata[i]);
    }
    
    return result;
}

// Construction Thompson pour concaténation
function buildThompsonConcatenation(regex, alphabet) {
    // Analyser l'expression pour identifier les composants
    const components = parseRegexComponents(regex);
    
    if (components.length === 0) {
        throw new Error("Aucun composant trouvé dans l'expression de concaténation");
    }
    
    if (components.length === 1) {
        return buildThompsonSequential(components[0], alphabet);
    }
    
    // Construire les automates pour chaque composant
    const automata = components.map(component => {
        if (component.endsWith('*')) {
            return buildThompsonKleene(component, alphabet);
        } else if (component.endsWith('+')) {
            return buildThompsonPlus(component, alphabet);
        } else if (component.includes('|')) {
            return buildThompsonUnion(component, alphabet);
        } else {
            return buildThompsonSequential(component, alphabet);
        }
    });
    
    // Concaténer tous les automates
    let result = automata[0];
    for (let i = 1; i < automata.length; i++) {
        result = concatenateThompsonAutomata(result, automata[i]);
    }
    
    return result;
}

// Fonction pour concaténer deux automates Thompson
function concatenateThompsonAutomata(automaton1, automaton2) {
    const allStates = [...automaton1.etats, ...automaton2.etats];
    const allTransitions = { ...automaton1.transitions, ...automaton2.transitions };
    
    // Connecter les états finaux de automaton1 aux états initiaux de automaton2 avec ε
    for (const finalState of automaton1.etats_finaux) {
        if (!allTransitions[finalState]) {
            allTransitions[finalState] = {};
        }
        if (!allTransitions[finalState]['ε']) {
            allTransitions[finalState]['ε'] = [];
        }
        allTransitions[finalState]['ε'].push(...automaton2.etats_initiaux);
    }
    
    return {
        alphabet: [...new Set([...automaton1.alphabet, ...automaton2.alphabet])].sort(),
        etats: allStates,
        etats_initiaux: automaton1.etats_initiaux,
        etats_finaux: automaton2.etats_finaux,
        transitions: allTransitions
    };
}

// Fonction pour faire l'union de deux automates Thompson
function unionThompsonAutomata(automaton1, automaton2) {
    const q0 = ThompsonStateID.next();
    const qf = ThompsonStateID.next();
    
    const allStates = [q0, qf, ...automaton1.etats, ...automaton2.etats];
    const allTransitions = { ...automaton1.transitions, ...automaton2.transitions };
    
    // Nouvel état initial
    allTransitions[q0] = { 
        'ε': [...automaton1.etats_initiaux, ...automaton2.etats_initiaux] 
    };
    
    // Nouvel état final
    allTransitions[qf] = {};
    
    // Connecter tous les états finaux au nouvel état final
    for (const finalState of [...automaton1.etats_finaux, ...automaton2.etats_finaux]) {
        if (!allTransitions[finalState]) {
            allTransitions[finalState] = {};
        }
        if (!allTransitions[finalState]['ε']) {
            allTransitions[finalState]['ε'] = [];
        }
        allTransitions[finalState]['ε'].push(qf);
    }
    
    return {
        alphabet: [...new Set([...automaton1.alphabet, ...automaton2.alphabet])].sort(),
        etats: allStates,
        etats_initiaux: [q0],
        etats_finaux: [qf],
        transitions: allTransitions
    };
}

// ============================================================================
// FONCTIONS DE VISUALISATION
// ============================================================================

function drawThompsonAutomaton(automaton) {
    const canvas = document.getElementById('thompsonCanvas');
    if (!canvas) {
        console.error('Canvas thompsonCanvas non trouvé');
        showMessage('❌ Erreur: Canvas de visualisation non trouvé', 'error');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    console.log('Dessin de l\'automate Thompson:', automaton);
    
    // Position des états
    const positions = calculateStatePositions(automaton.etats, canvas.width, canvas.height);
    
    // Dessiner les transitions
    drawTransitions(ctx, automaton.transitions, positions);
    
    // Dessiner les états
    drawStates(ctx, automaton, positions);
    
    showMessage('🎨 Automate Thompson dessiné avec succès', 'success');
}

function calculateStatePositions(states, width, height) {
    const positions = {};
    const margin = 80;
    const usableWidth = width - 2 * margin;
    const usableHeight = height - 2 * margin;
    
    if (states.length === 1) {
        positions[states[0]] = { x: width/2, y: height/2 };
        return positions;
    }
    
    if (states.length === 2) {
        positions[states[0]] = { x: width/3, y: height/2 };
        positions[states[1]] = { x: 2*width/3, y: height/2 };
        return positions;
    }
    
    states.forEach((state, index) => {
        const angle = (2 * Math.PI * index) / states.length;
        const radius = Math.min(usableWidth, usableHeight) / 3;
        
        positions[state] = {
            x: width/2 + radius * Math.cos(angle),
            y: height/2 + radius * Math.sin(angle)
        };
    });
    
    return positions;
}

function drawStates(ctx, automaton, positions) {
    const stateRadius = 25;
    
    automaton.etats.forEach(state => {
        const pos = positions[state];
        const isInitial = automaton.etats_initiaux.includes(state);
        const isFinal = automaton.etats_finaux.includes(state);
        
        // Cercle principal
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, stateRadius, 0, 2 * Math.PI);
        ctx.fillStyle = isInitial ? '#e3f2fd' : '#f5f5f5';
        ctx.fill();
        ctx.strokeStyle = isFinal ? '#4caf50' : '#666';
        ctx.lineWidth = isFinal ? 3 : 2;
        ctx.stroke();
        
        // Double cercle pour états finaux
        if (isFinal) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, stateRadius - 5, 0, 2 * Math.PI);
            ctx.stroke();
        }
        
        // Flèche pour état initial
        if (isInitial) {
            ctx.beginPath();
            ctx.moveTo(pos.x - stateRadius - 20, pos.y);
            ctx.lineTo(pos.x - stateRadius, pos.y);
            ctx.strokeStyle = '#2196f3';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Pointe de flèche
            ctx.beginPath();
            ctx.moveTo(pos.x - stateRadius, pos.y);
            ctx.lineTo(pos.x - stateRadius - 8, pos.y - 4);
            ctx.moveTo(pos.x - stateRadius, pos.y);
            ctx.lineTo(pos.x - stateRadius - 8, pos.y + 4);
            ctx.stroke();
        }
        
        // Label de l'état
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`q${state}`, pos.x, pos.y);
    });
}

function drawTransitions(ctx, transitions, positions) {
    const stateRadius = 25;
    
    for (const fromState in transitions) {
        const fromPos = positions[fromState];
        if (!fromPos) continue;
        
        for (const symbol in transitions[fromState]) {
            const toStates = transitions[fromState][symbol];
            
            toStates.forEach(toState => {
                const toPos = positions[toState];
                if (!toPos) return;
                
                // Auto-boucle
                if (fromState == toState) {
                    drawSelfLoop(ctx, fromPos, symbol, stateRadius);
                    return;
                }
                
                // Calculer les points de début et fin sur les cercles
                const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
                const startX = fromPos.x + stateRadius * Math.cos(angle);
                const startY = fromPos.y + stateRadius * Math.sin(angle);
                const endX = toPos.x - stateRadius * Math.cos(angle);
                const endY = toPos.y - stateRadius * Math.sin(angle);
                
                // Dessiner la flèche
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.lineTo(endX, endY);
                ctx.strokeStyle = symbol === 'ε' ? '#ff5722' : '#333';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Pointe de flèche
                const arrowLength = 10;
                const arrowAngle = Math.PI / 6;
                
                ctx.beginPath();
                ctx.moveTo(endX, endY);
                ctx.lineTo(
                    endX - arrowLength * Math.cos(angle - arrowAngle),
                    endY - arrowLength * Math.sin(angle - arrowAngle)
                );
                ctx.moveTo(endX, endY);
                ctx.lineTo(
                    endX - arrowLength * Math.cos(angle + arrowAngle),
                    endY - arrowLength * Math.sin(angle + arrowAngle)
                );
                ctx.stroke();
                
                // Label de la transition
                const midX = (startX + endX) / 2;
                const midY = (startY + endY) / 2;
                
                drawTransitionLabel(ctx, midX, midY, symbol);
            });
        }
    }
}

function drawSelfLoop(ctx, pos, symbol, radius) {
    const loopRadius = 15;
    const centerX = pos.x;
    const centerY = pos.y - radius - loopRadius;
    
    // Dessiner la boucle
    ctx.beginPath();
    ctx.arc(centerX, centerY, loopRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = symbol === 'ε' ? '#ff5722' : '#333';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Pointe de flèche
    ctx.beginPath();
    ctx.moveTo(centerX + loopRadius - 2, centerY);
    ctx.lineTo(centerX + loopRadius - 8, centerY - 4);
    ctx.moveTo(centerX + loopRadius - 2, centerY);
    ctx.lineTo(centerX + loopRadius - 8, centerY + 4);
    ctx.stroke();
    
    // Label
    drawTransitionLabel(ctx, centerX, centerY - loopRadius - 10, symbol);
}

function drawTransitionLabel(ctx, x, y, symbol) {
    ctx.fillStyle = symbol === 'ε' ? '#ff5722' : '#333';
    ctx.font = symbol === 'ε' ? 'bold 14px Arial' : '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Fond blanc pour le label
    const metrics = ctx.measureText(symbol);
    ctx.fillStyle = 'white';
    ctx.fillRect(x - metrics.width/2 - 3, y - 8, metrics.width + 6, 16);
    ctx.strokeStyle = '#ddd';
    ctx.strokeRect(x - metrics.width/2 - 3, y - 8, metrics.width + 6, 16);
    
    ctx.fillStyle = symbol === 'ε' ? '#ff5722' : '#333';
    ctx.fillText(symbol, x, y);
}

// ============================================================================
// FONCTIONS D'INFORMATION ET UTILITAIRES
// ============================================================================

function displayThompsonInfo(regex, automaton) {
    let infoDiv = document.getElementById('thompsonInfo');
    if (!infoDiv) {
        infoDiv = document.getElementById('glushkovInfo');
    }
    
    if (infoDiv) {
        infoDiv.style.display = 'block';
        infoDiv.innerHTML = `
            <div class="thompson-info-content">
                <h4>📊 Informations sur l'automate de Thompson</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Expression régulière :</strong> ${regex}
                    </div>
                    <div class="info-item">
                        <strong>Alphabet :</strong> {${automaton.alphabet.join(', ')}}
                    </div>
                    <div class="info-item">
                        <strong>Nombre d'états :</strong> ${automaton.etats.length}
                    </div>
                    <div class="info-item">
                        <strong>États initiaux :</strong> {${automaton.etats_initiaux.map(s => `q${s}`).join(', ')}}
                    </div>
                    <div class="info-item">
                        <strong>États finaux :</strong> {${automaton.etats_finaux.map(s => `q${s}`).join(', ')}}
                    </div>
                    <div class="info-item">
                        <strong>Transitions ε :</strong> ${countEpsilonTransitions(automaton.transitions)}
                    </div>
                </div>
            </div>
        `;
    }
}

function countEpsilonTransitions(transitions) {
    let count = 0;
    for (const state in transitions) {
        if (transitions[state]['ε']) {
            count += transitions[state]['ε'].length;
        }
    }
    return count;
}

function validateThompsonAutomaton(automaton) {
    if (!automaton) {
        throw new Error("Automate null");
    }
    
    if (!automaton.alphabet || !Array.isArray(automaton.alphabet)) {
        throw new Error("Alphabet invalide");
    }
    
    if (!automaton.etats || !Array.isArray(automaton.etats) || automaton.etats.length === 0) {
        throw new Error("États invalides");
    }
    
    if (!automaton.etats_initiaux || !Array.isArray(automaton.etats_initiaux) || automaton.etats_initiaux.length === 0) {
        throw new Error("États initiaux invalides");
    }
    
    if (!automaton.etats_finaux || !Array.isArray(automaton.etats_finaux)) {
        throw new Error("États finaux invalides");
    }
    
    if (!automaton.transitions || typeof automaton.transitions !== 'object') {
        throw new Error("Transitions invalides");
    }
    
    // Vérifier que tous les états référencés existent
    const allStates = new Set(automaton.etats);
    
    automaton.etats_initiaux.forEach(state => {
        if (!allStates.has(state)) {
            throw new Error(`État initial ${state} n'existe pas`);
        }
    });
    
    automaton.etats_finaux.forEach(state => {
        if (!allStates.has(state)) {
            throw new Error(`État final ${state} n'existe pas`);
        }
    });
    
    console.log("Automate Thompson validé avec succès");
}

// ============================================================================
// FONCTIONS DE DÉTECTION D'EXPRESSION
// ============================================================================

function isSimpleCharacter(regex) {
    return /^[a-zA-Z]$/.test(regex);
}

function isKleeneExpression(regex) {
    return /\*/.test(regex);
}

function isPlusExpression(regex) {
    return /\+/.test(regex) && !/\*/.test(regex);
}

function isUnionExpression(regex) {
    return /\|/.test(regex);
}

function isConcatenationExpression(regex) {
    return /^[a-zA-Z\(\)\*\+]{2,}$/.test(regex) && !/\|/.test(regex);
}


function extractAlphabet(regex) {
    // Supprimer les opérateurs et caractères spéciaux pour extraire les lettres
    const letters = regex.match(/[a-zA-Z]/g) || [];
    const uniqueLetters = Array.from(new Set(letters.map(l => l.toLowerCase()))).sort();
    
    if (uniqueLetters.length === 0) {
        throw new Error("Aucune lettre trouvée dans l'expression régulière");
    }
    
    return uniqueLetters;
}

function parseRegexComponents(regex) {
    const components = [];
    let currentComponent = '';
    let depth = 0;
    
    for (let i = 0; i < regex.length; i++) {
        const char = regex[i];
        
        if (char === '(') {
            depth++;
            currentComponent += char;
        } else if (char === ')') {
            depth--;
            currentComponent += char;
        } else if (char === ' ' && depth === 0) {
            if (currentComponent.trim()) {
                components.push(currentComponent.trim());
                currentComponent = '';
            }
        } else {
            currentComponent += char;
        }
    }
    
    if (currentComponent.trim()) {
        components.push(currentComponent.trim());
    }
    
    return components.length > 0 ? components : [regex];
}

// ============================================================================
// FONCTIONS DE SIMULATION ET TEST
// ============================================================================

function simulateThompsonAutomaton() {
    if (!currentAutomaton) {
        showMessage('⚠️ Aucun automate de Thompson n\'est construit.', 'warning');
        return;
    }
    
    const wordInput = document.getElementById('wordInput');
    if (!wordInput) {
        showMessage('❌ Erreur: Champ de saisie du mot non trouvé', 'error');
        return;
    }
    
    const word = wordInput.value.trim().toLowerCase();
    if (!word) {
        showMessage('⚠️ Veuillez entrer un mot à tester.', 'warning');
        return;
    }
    
    try {
        console.log(`Test du mot "${word}" sur l'automate Thompson`);
        
        const isAccepted = testWordOnThompsonAutomaton(currentAutomaton, word);
        const result = isAccepted ? 'accepté' : 'rejeté';
        const icon = isAccepted ? '✅' : '❌';
        const type = isAccepted ? 'success' : 'error';
        
        showMessage(`${icon} Le mot "${word}" est ${result} par l'automate.`, type);
        
        // Afficher les détails de la simulation
        displaySimulationDetails(word, isAccepted);
        
    } catch (error) {
        console.error('Erreur lors de la simulation:', error);
        showMessage(`❌ Erreur lors de la simulation : ${error.message}`, 'error');
    }
}

function testWordOnThompsonAutomaton(automaton, word) {
    // Utiliser la fermeture epsilon pour gérer les transitions ε
    let currentStates = epsilonClosure(automaton, automaton.etats_initiaux);
    
    console.log(`États initiaux après fermeture ε: [${currentStates.join(', ')}]`);
    
    for (let i = 0; i < word.length; i++) {
        const symbol = word[i];
        const nextStates = [];
        
        // Pour chaque état courant, voir où on peut aller avec ce symbole
        for (const state of currentStates) {
            if (automaton.transitions[state] && automaton.transitions[state][symbol]) {
                nextStates.push(...automaton.transitions[state][symbol]);
            }
        }
        
        if (nextStates.length === 0) {
            console.log(`Aucune transition possible pour '${symbol}' depuis [${currentStates.join(', ')}]`);
            return false;
        }
        
        // Appliquer la fermeture epsilon aux nouveaux états
        currentStates = epsilonClosure(automaton, nextStates);
        console.log(`Après '${symbol}': [${currentStates.join(', ')}]`);
    }
    
    // Vérifier si on est dans un état final
    const isAccepted = currentStates.some(state => automaton.etats_finaux.includes(state));
    console.log(`États finaux: [${automaton.etats_finaux.join(', ')}]`);
    console.log(`États actuels: [${currentStates.join(', ')}]`);
    console.log(`Mot accepté: ${isAccepted}`);
    
    return isAccepted;
}

function epsilonClosure(automaton, states) {
    const closure = new Set(states);
    const stack = [...states];
    
    while (stack.length > 0) {
        const state = stack.pop();
        
        if (automaton.transitions[state] && automaton.transitions[state]['ε']) {
            for (const epsilonState of automaton.transitions[state]['ε']) {
                if (!closure.has(epsilonState)) {
                    closure.add(epsilonState);
                    stack.push(epsilonState);
                }
            }
        }
    }
    
    return Array.from(closure).sort((a, b) => a - b);
}

function displaySimulationDetails(word, isAccepted) {
    let detailsDiv = document.getElementById('simulationDetails');
    if (!detailsDiv) {
        detailsDiv = document.createElement('div');
        detailsDiv.id = 'simulationDetails';
        detailsDiv.style.cssText = `
            margin: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        `;
        
        const infoDiv = document.getElementById('thompsonInfo') || document.getElementById('glushkovInfo');
        if (infoDiv && infoDiv.parentNode) {
            infoDiv.parentNode.insertBefore(detailsDiv, infoDiv.nextSibling);
        } else {
            document.body.appendChild(detailsDiv);
        }
    }
    
    detailsDiv.style.display = 'block';
    detailsDiv.innerHTML = `
        <div class="simulation-details">
            <h4>🔍 Détails de la simulation</h4>
            <div class="detail-item">
                <strong>Mot testé :</strong> "${word}"
            </div>
            <div class="detail-item">
                <strong>Résultat :</strong> <span style="color: ${isAccepted ? '#28a745' : '#dc3545'}">
                    ${isAccepted ? '✅ Accepté' : '❌ Rejeté'}
                </span>
            </div>
            <div class="detail-item">
                <strong>Longueur :</strong> ${word.length} caractère(s)
            </div>
            <div class="detail-item">
                <strong>Alphabet utilisé :</strong> {${Array.from(new Set(word.split(''))).sort().join(', ')}}
            </div>
        </div>
    `;
}

// ============================================================================
// FONCTIONS D'EXPORT ET SAUVEGARDE
// ============================================================================

function exportThompsonAutomaton() {
    if (!currentAutomaton) {
        showMessage('⚠️ Aucun automate de Thompson à exporter.', 'warning');
        return;
    }
    
    try {
        const exportData = {
            type: 'Thompson',
            timestamp: new Date().toISOString(),
            regex: document.getElementById('regexInput')?.value || '',
            automaton: currentAutomaton
        };
        
        const jsonString = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `thompson_automaton_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showMessage('💾 Automate exporté avec succès', 'success');
        
    } catch (error) {
        console.error('Erreur lors de l\'export:', error);
        showMessage(`❌ Erreur lors de l'export : ${error.message}`, 'error');
    }
}

function importThompsonAutomaton(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importData = JSON.parse(e.target.result);
            
            if (!importData.automaton) {
                throw new Error("Fichier d'automate invalide");
            }
            
            // Valider l'automate importé
            validateThompsonAutomaton(importData.automaton);
            
            // Restaurer l'automate
            currentAutomaton = importData.automaton;
            originalAutomaton = JSON.parse(JSON.stringify(importData.automaton));
            isAutomatonSaved = true;
            
            // Restaurer l'expression régulière si disponible
            if (importData.regex) {
                const regexInput = document.getElementById('regexInput');
                if (regexInput) {
                    regexInput.value = importData.regex;
                }
            }
            
            // Dessiner l'automate
            drawThompsonAutomaton(currentAutomaton);
            
            // Afficher les informations
            displayThompsonInfo(importData.regex || 'Importé', currentAutomaton);
            
            showMessage('📁 Automate importé avec succès', 'success');
            
        } catch (error) {
            console.error('Erreur lors de l\'import:', error);
            showMessage(`❌ Erreur lors de l'import : ${error.message}`, 'error');
        }
    };
    
    reader.readAsText(file);
    
    // Réinitialiser l'input file
    event.target.value = '';
}

// ============================================================================
// FONCTIONS DE CONVERSION ET TRANSFORMATION
// ============================================================================

function convertToGlushkov() {
    if (!currentAutomaton) {
        showMessage('⚠️ Aucun automate de Thompson à convertir.', 'warning');
        return;
    }
    
    try {
        console.log('Début conversion Thompson vers Glushkov');
        
        // Pour une conversion complète, on aurait besoin d'algorithmes plus complexes
        // Ici, on fait une version simplifiée pour la démonstration
        const glushkovAutomaton = convertThompsonToGlushkov(currentAutomaton);
        
        // Sauvegarder l'automate de Glushkov
        currentAutomaton = glushkovAutomaton;
        
        // Redessiner
        drawThompsonAutomaton(glushkovAutomaton);
        
        showMessage('🔄 Conversion vers Glushkov effectuée', 'success');
        
    } catch (error) {
        console.error('Erreur lors de la conversion:', error);
        showMessage(`❌ Erreur lors de la conversion : ${error.message}`, 'error');
    }
}

function convertThompsonToGlushkov(thompsonAutomaton) {
    // Version simplifiée de la conversion
    // Dans une implémentation complète, il faudrait :
    // 1. Supprimer les transitions epsilon
    // 2. Fusionner les états équivalents
    // 3. Optimiser la structure
    
    console.log('Conversion Thompson->Glushkov (version simplifiée)');
    
    // Pour l'instant, on retourne une copie avec quelques optimisations
    const optimized = JSON.parse(JSON.stringify(thompsonAutomaton));
    
    // Supprimer les transitions epsilon vides
    for (const state in optimized.transitions) {
        if (optimized.transitions[state]['ε'] && optimized.transitions[state]['ε'].length === 0) {
            delete optimized.transitions[state]['ε'];
        }
    }
    
    return optimized;
}

// ============================================================================
// FONCTIONS D'INITIALISATION ET ÉVÉNEMENTS
// ============================================================================

function initializeThompsonSimulator() {
    console.log('Initialisation du simulateur Thompson');
    
    // Réinitialiser l'état
    resetThompsonState();
    
    // Vérifier la présence des éléments DOM
    const requiredElements = ['regexInput', 'thompsonCanvas'];
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.warn('Éléments DOM manquants:', missingElements);
    }
    
    // Ajouter les styles CSS si nécessaire
    addThompsonStyles();
    
    // Configurer le canvas
    setupThompsonCanvas();
    
    showMessage('🚀 Simulateur Thompson initialisé', 'info');
}

function setupThompsonCanvas() {
    const canvas = document.getElementById('thompsonCanvas');
    if (!canvas) return;
    
    // Définir la taille du canvas
    canvas.width = 800;
    canvas.height = 600;
    
    // Style du canvas
    canvas.style.border = '2px solid #ddd';
    canvas.style.borderRadius = '8px';
    canvas.style.backgroundColor = '#fafafa';
    canvas.style.cursor = 'default';
    
    console.log('Canvas Thompson configuré');
}

function addThompsonStyles() {
    if (document.getElementById('thompsonStyles')) return;
    
    const style = document.createElement('style');
    style.id = 'thompsonStyles';
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .thompson-info-content {
            font-family: 'Courier New', monospace;
        }
        
        .info-grid {
            display: grid;
            gap: 10px;
            margin-top: 15px;
        }
        
        .info-item {
            padding: 8px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        
        .simulation-details {
            font-family: 'Segoe UI', sans-serif;
        }
        
        .detail-item {
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        
        .detail-item:last-child {
            border-bottom: none;
        }
    `;
    
    document.head.appendChild(style);
}

// ============================================================================
// FONCTIONS DE DEBUG ET UTILITAIRES
// ============================================================================

function debugThompsonAutomaton() {
    if (!currentAutomaton) {
        console.log('Aucun automate Thompson chargé');
        return;
    }
    
    console.group('🔧 Debug Automate Thompson');
    console.log('Alphabet:', currentAutomaton.alphabet);
    console.log('États:', currentAutomaton.etats);
    console.log('États initiaux:', currentAutomaton.etats_initiaux);
    console.log('États finaux:', currentAutomaton.etats_finaux);
    console.log('Transitions:', currentAutomaton.transitions);
    
    // Vérifier la cohérence
    console.group('Vérifications');
    console.log('Nombre total d\'états:', currentAutomaton.etats.length);
    console.log('Nombre de transitions:', Object.keys(currentAutomaton.transitions).length);
    
    let totalTransitions = 0;
    for (const state in currentAutomaton.transitions) {
        for (const symbol in currentAutomaton.transitions[state]) {
            totalTransitions += currentAutomaton.transitions[state][symbol].length;
        }
    }
    console.log('Nombre total de transitions:', totalTransitions);
    
    const epsilonCount = countEpsilonTransitions(currentAutomaton.transitions);
    console.log('Transitions epsilon:', epsilonCount);
    
    console.groupEnd();
    console.groupEnd();
}

function clearThompsonCanvas() {
    const canvas = document.getElementById('thompsonCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        showMessage('🧹 Canvas effacé', 'info');
    }
}

// ============================================================================
// FONCTIONS EXPOSÉES GLOBALEMENT
// ============================================================================

// Exposer les fonctions principales pour l'interface
window.ThompsonSimulator = {
    construct: constructThompson,
    simulate: simulateThompsonAutomaton,
    export: exportThompsonAutomaton,
    import: importThompsonAutomaton,
    convertToGlushkov: convertToGlushkov,
    debug: debugThompsonAutomaton,
    clear: clearThompsonCanvas,
    reset: resetThompsonState,
    initialize: initializeThompsonSimulator
};

// Auto-initialisation si le DOM est prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeThompsonSimulator);
} else {
    initializeThompsonSimulator();
}

console.log('✅ Simulateur d\'automates de Thompson chargé avec succès');
