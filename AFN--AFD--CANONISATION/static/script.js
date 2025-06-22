document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('automateCanvas');
    ctx = canvas.getContext('2d');
    
    // Ajuster la taille du canvas
    resizeCanvas();
    
    // Événements de souris pour le zoom et pan
    canvas.addEventListener('wheel', handleWheel);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);
    
    // Redimensionnement du canvas
    window.addEventListener('resize', resizeCanvas);
    
    // Charger l'exemple par défaut
    loadExample('complex');
});

// Variables globales
let currentAutomate = null;
let currentAFD = null;
let canvas = null;
let ctx = null;
let scale = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;

// Gestion du canvas
function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 40;
    canvas.height = Math.max(400, container.clientHeight - 40);
    if (currentAutomate) {
        drawAutomate(currentAutomate);
    }
}

function handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale *= delta;
    scale = Math.max(0.1, Math.min(3, scale));
    if (currentAutomate) {
        drawAutomate(currentAutomate);
    }
}

function handleMouseDown(e) {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    canvas.style.cursor = 'grabbing';
}

function handleMouseMove(e) {
    if (isDragging) {
        const deltaX = e.clientX - lastMouseX;
        const deltaY = e.clientY - lastMouseY;
        offsetX += deltaX;
        offsetY += deltaY;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        if (currentAutomate) {
            drawAutomate(currentAutomate);
        }
    }
}

function handleMouseUp() {
    isDragging = false;
    canvas.style.cursor = 'crosshair';
}

function resetZoom() {
    scale = 1;
    offsetX = 0;
    offsetY = 0;
    if (currentAutomate) {
        drawAutomate(currentAutomate);
    }
}

// Création et gestion des automates
function createAutomate() {
    try {
        const alphabet = parseInput(document.getElementById('alphabet').value);
        const etats = parseInput(document.getElementById('etats').value);
        const etatInitial = document.getElementById('etatInitial').value.trim();
        const etatsFinaux = parseInput(document.getElementById('etatsFinaux').value);
        const transitionsText = document.getElementById('transitions').value.trim();
        
        let transitions;
        try {
            transitions = JSON.parse(transitionsText);
        } catch (e) {
            throw new Error('Format JSON invalide pour les transitions');
        }
        
        // Validation
        if (!alphabet.length) throw new Error('L\'alphabet ne peut pas être vide');
        if (!etats.length) throw new Error('Les états ne peuvent pas être vides');
        if (!etatInitial) throw new Error('L\'état initial doit être spécifié');
        if (!etats.includes(etatInitial)) throw new Error('L\'état initial doit être dans la liste des états');
        
        // Créer l'automate
        currentAutomate = {
            alphabet: alphabet,
            etats: etats,
            transitions: transitions,
            etat_initial: etatInitial,
            etats_final: etatsFinaux,
            type: isAFD(transitions) ? 'AFD' : 'AFN'
        };
        
        // Activer les boutons
        document.getElementById('convertBtn').disabled = currentAutomate.type === 'AFD';
        document.getElementById('testBtn').disabled = false;
        
        // Afficher les informations
        updateAutomateInfo(currentAutomate);
        
        // Dessiner l'automate
        drawAutomate(currentAutomate);
        
        showMessage('Automate créé avec succès (Type: ' + currentAutomate.type + ')', 'success');
        
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

function parseInput(input) {
    return input.split(',').map(s => s.trim()).filter(s => s.length > 0);
}

function isAFD(transitions) {
    for (let etat in transitions) {
        for (let symbole in transitions[etat]) {
            const destinations = transitions[etat][symbole];
            if (Array.isArray(destinations) && destinations.length > 1) {
                return false;
            }
        }
    }
    return true;
}

// Conversion AFN → AFD
function convertToAFD() {
    if (!currentAutomate || currentAutomate.type === 'AFD') {
        showMessage('Aucun AFN à convertir', 'warning');
        return;
    }
    
    try {
        const afd = convertAFNtoAFD(currentAutomate);
        currentAFD = afd;
        
        // Afficher les informations de l'AFD
        document.getElementById('afdPanel').style.display = 'block';
        updateAFDInfo(afd);
        
        showMessage('Conversion AFN → AFD réussie', 'success');
        
    } catch (error) {
        showMessage('Erreur lors de la conversion: ' + error.message, 'error');
    }
}

function convertAFNtoAFD(afn) {
    const nouveaux_etats = [];
    const nouvelles_transitions = {};
    const nouveaux_finaux = [];
    
    const queue = [];
    const traites = new Set();
    
    // État initial de l'AFD
    const etat_initial_afd = new Set([afn.etat_initial]);
    const etat_initial_str = setToString(etat_initial_afd);
    
    queue.push(etat_initial_afd);
    nouveaux_etats.push(etat_initial_str);
    
    while (queue.length > 0) {
        const etat_courant = queue.shift();
        const etat_courant_str = setToString(etat_courant);
        
        if (traites.has(etat_courant_str)) {
            continue;
        }
        traites.add(etat_courant_str);
        
        // Pour chaque symbole de l'alphabet
        for (const symbole of afn.alphabet) {
            const nouvel_etat = new Set();
            
            for (const etat of etat_courant) {
                if (afn.transitions[etat] && afn.transitions[etat][symbole]) {
                    const destinations = afn.transitions[etat][symbole];
                    if (Array.isArray(destinations)) {
                        destinations.forEach(dest => nouvel_etat.add(dest));
                    } else {
                        nouvel_etat.add(destinations);
                    }
                }
            }
            
            if (nouvel_etat.size > 0) {
                const nouvel_etat_str = setToString(nouvel_etat);
                
                // Ajouter la transition
                if (!nouvelles_transitions[etat_courant_str]) {
                    nouvelles_transitions[etat_courant_str] = {};
                }
                nouvelles_transitions[etat_courant_str][symbole] = nouvel_etat_str;
                
                // Ajouter le nouvel état s'il n'existe pas déjà
                if (!nouveaux_etats.includes(nouvel_etat_str)) {
                    nouveaux_etats.push(nouvel_etat_str);
                    queue.push(nouvel_etat);
                }
            }
        }
    }
    
    // Déterminer les états finaux de l'AFD
    for (const etat_str of nouveaux_etats) {
        const etat_set = stringToSet(etat_str);
        for (const e of etat_set) {
            if (afn.etats_final.includes(e)) {
                nouveaux_finaux.push(etat_str);
                break;
            }
        }
    }
    
    return {
        alphabet: afn.alphabet,
        etats: nouveaux_etats,
        transitions: nouvelles_transitions,
        etat_initial: etat_initial_str,
        etats_final: nouveaux_finaux,
        type: 'AFD'
    };
}

// Canonisation d'automate
function canonizeAutomate() {
    if (!currentAutomate) {
        showMessage('Aucun automate à canoniser', 'warning');
        return;
    }
    
    try {
        const automateCanonique = canonizeAutomateFunction(currentAutomate);
        
        // Mettre à jour les champs du formulaire
        document.getElementById('alphabet').value = automateCanonique.alphabet.join(',');
        document.getElementById('etats').value = automateCanonique.etats.join(',');
        document.getElementById('etatInitial').value = automateCanonique.etat_initial;
        document.getElementById('etatsFinaux').value = automateCanonique.etats_final.join(',');
        document.getElementById('transitions').value = JSON.stringify(automateCanonique.transitions, null, 2);
        
        // Recréer l'automate avec les nouvelles valeurs
        currentAutomate = automateCanonique;
        
        // Mettre à jour l'affichage
        updateAutomateInfo(currentAutomate);
        drawAutomate(currentAutomate);
        
        showMessage('Automate canonisé avec succès', 'success');
        
    } catch (error) {
        showMessage('Erreur lors de la canonisation: ' + error.message, 'error');
    }
}

function canonizeAutomateFunction(automate) {
    // Créer un mapping des anciens états vers les nouveaux états canoniques
    const mapping = {};
    const etats_tries = [...automate.etats].sort();
    
    // L'état initial devient toujours q0
    mapping[automate.etat_initial] = 'q0';
    let compteur = 1;
    
    // Mapper les autres états
    for (const etat of etats_tries) {
        if (etat !== automate.etat_initial) {
            mapping[etat] = 'q' + compteur;
            compteur++;
        }
    }
    
    // Créer les nouveaux états
    const nouveaux_etats = Object.values(mapping).sort();
    
    // Créer les nouvelles transitions
    const nouvelles_transitions = {};
    for (const [ancien_etat, nouveau_etat] of Object.entries(mapping)) {
        if (automate.transitions[ancien_etat]) {
            nouvelles_transitions[nouveau_etat] = {};
            for (const [symbole, destinations] of Object.entries(automate.transitions[ancien_etat])) {
                if (Array.isArray(destinations)) {
                    nouvelles_transitions[nouveau_etat][symbole] = destinations.map(dest => mapping[dest]).sort();
                } else {
                    nouvelles_transitions[nouveau_etat][symbole] = mapping[destinations];
                }
            }
        }
    }
    
    // Créer les nouveaux états finaux
    const nouveaux_finaux = automate.etats_final.map(etat => mapping[etat]).sort();
    
    return {
        alphabet: [...automate.alphabet].sort(),
        etats: nouveaux_etats,
        transitions: nouvelles_transitions,
        etat_initial: mapping[automate.etat_initial],
        etats_final: nouveaux_finaux,
        type: automate.type
    };
}

// Fonctions utilitaires pour les ensembles
function setToString(set) {
    return '{' + Array.from(set).sort().join(',') + '}';
}

function stringToSet(str) {
    if (str === '{}') return new Set();
    return new Set(str.slice(1, -1).split(','));
}

// Test de mots
function testWord() {
    const word = document.getElementById('testWord').value.trim();
    if (!currentAutomate) {
        showMessage('Aucun automate créé', 'warning');
        return;
    }
    
    try {
        const result = testWordInAutomate(currentAutomate, word);
        displayTestResult(result, word);
    } catch (error) {
        showMessage('Erreur lors du test: ' + error.message, 'error');
    }
}

function testWordInAutomate(automate, word) {
    if (automate.type === 'AFD') {
        return testWordAFD(automate, word);
    } else {
        return testWordAFN(automate, word);
    }
}

function testWordAFD(automate, word) {
    let etat_courant = automate.etat_initial;
    const chemin = [etat_courant];
    
    for (const symbole of word) {
        if (automate.transitions[etat_courant] && automate.transitions[etat_courant][symbole]) {
            etat_courant = automate.transitions[etat_courant][symbole];
            chemin.push(etat_courant);
        } else {
            return { accepte: false, chemin: chemin };
        }
    }
    
    return { 
        accepte: automate.etats_final.includes(etat_courant), 
        chemin: chemin 
    };
}

function testWordAFN(automate, word) {
    function explorer(etat, index, chemin) {
        if (index === word.length) {
            return { 
                accepte: automate.etats_final.includes(etat), 
                chemin: chemin 
            };
        }
        
        const symbole = word[index];
        if (automate.transitions[etat] && automate.transitions[etat][symbole]) {
            const destinations = automate.transitions[etat][symbole];
            if (Array.isArray(destinations)) {
                for (const dest of destinations) {
                    const result = explorer(dest, index + 1, [...chemin, dest]);
                    if (result.accepte) {
                        return result;
                    }
                }
            } else {
                return explorer(destinations, index + 1, [...chemin, destinations]);
            }
        }
        
        return { accepte: false, chemin: chemin };
    }
    
    return explorer(automate.etat_initial, 0, [automate.etat_initial]);
}

function displayTestResult(result, word) {
    const resultDiv = document.getElementById('testResult');
    const className = result.accepte ? 'success' : 'error';
    const message = result.accepte ? 'accepté' : 'rejeté';
    
    resultDiv.innerHTML = `
        <div class="test-result ${className}">
            <strong>Mot "${word}" ${message}</strong><br>
            Chemin: ${result.chemin.join(' → ')}
        </div>
    `;
}

// Validation d'automate
function validateAutomate() {
    if (!currentAutomate) {
        showMessage('Aucun automate à valider', 'warning');
        return;
    }
    
    const errors = [];
    const warnings = [];
    
    // Vérifications de base
    if (!currentAutomate.alphabet.length) {
        errors.push('L\'alphabet ne peut pas être vide');
    }
    
    if (!currentAutomate.etats.length) {
        errors.push('La liste des états ne peut pas être vide');
    }
    
    if (!currentAutomate.etat_initial) {
        errors.push('L\'état initial doit être spécifié');
    }
    
    if (!currentAutomate.etats_final.length) {
        warnings.push('Aucun état final spécifié');
    }
    
    // Vérifier que l'état initial existe
    if (!currentAutomate.etats.includes(currentAutomate.etat_initial)) {
        errors.push('L\'état initial doit être dans la liste des états');
    }
    
    // Vérifier que les états finaux existent
    for (const etat of currentAutomate.etats_final) {
        if (!currentAutomate.etats.includes(etat)) {
            errors.push(`L'état final "${etat}" n'existe pas dans la liste des états`);
        }
    }
    
    // Vérifier les transitions
    for (const [etat, transitions] of Object.entries(currentAutomate.transitions)) {
        if (!currentAutomate.etats.includes(etat)) {
            errors.push(`L'état "${etat}" dans les transitions n'existe pas`);
        }
        
        for (const [symbole, destinations] of Object.entries(transitions)) {
            if (!currentAutomate.alphabet.includes(symbole)) {
                errors.push(`Le symbole "${symbole}" n'est pas dans l'alphabet`);
            }
            
            if (Array.isArray(destinations)) {
                for (const dest of destinations) {
                    if (!currentAutomate.etats.includes(dest)) {
                        errors.push(`L'état destination "${dest}" n'existe pas`);
                    }
                }
            } else {
                if (!currentAutomate.etats.includes(destinations)) {
                    errors.push(`L'état destination "${destinations}" n'existe pas`);
                }
            }
        }
    }
    
    // Afficher les résultats
    let message = '';
    if (errors.length === 0) {
        message = 'Automate valide ✅';
        if (warnings.length > 0) {
            message += '<br>Avertissements: ' + warnings.join(', ');
        }
        showMessage(message, 'success');
    } else {
        message = 'Erreurs trouvées: ' + errors.join(', ');
        if (warnings.length > 0) {
            message += '<br>Avertissements: ' + warnings.join(', ');
        }
        showMessage(message, 'error');
    }
}

// Exemples prédéfinis
function loadExample(type) {
    const examples = {
        'simple': {
            alphabet: 'a,b',
            etats: 'q0,q1,q2',
            etat_initial: 'q0',
            etats_final: 'q2',
            transitions: `{
  "q0": {"a": ["q1"], "b": ["q0"]},
  "q1": {"a": ["q2"], "b": ["q1"]},
  "q2": {"a": ["q2"], "b": ["q2"]}
}`
        },
        'complex': {
            alphabet: 'a,b',
            etats: '1,2,3,4',
            etat_initial: '1',
            etats_final: '4',
            transitions: `{
  "1": {"a": ["1", "2"]}, 
  "2": {"a": ["4"], "b": ["3"]}, 
  "3": {"b": ["3", "4"]}
}`
        },
        'binary': {
            alphabet: '0,1',
            etats: 'q0,q1,q2',
            etat_initial: 'q0',
            etats_final: 'q2',
            transitions: `{
  "q0": {"0": ["q0"], "1": ["q0", "q1"]},
  "q1": {"0": ["q2"], "1": ["q2"]},
  "q2": {}
}`
        }
    };
    
    const example = examples[type];
    if (example) {
        document.getElementById('alphabet').value = example.alphabet;
        document.getElementById('etats').value = example.etats;
        document.getElementById('etatInitial').value = example.etat_initial;
        document.getElementById('etatsFinaux').value = example.etats_final;
        document.getElementById('transitions').value = example.transitions;
        
        createAutomate();
    }
}

// Fonctions d'affichage
function updateAutomateInfo(automate) {
    const infoDiv = document.getElementById('automateInfo');
    infoDiv.innerHTML = `
        <div class="automate-info">
            <div class="info-card">
                <h3>Informations générales</h3>
                <ul>
                    <li><strong>Type:</strong> ${automate.type}</li>
                    <li><strong>États:</strong> ${automate.etats.length}</li>
                    <li><strong>Alphabet:</strong> {${automate.alphabet.join(', ')}}</li>
                    <li><strong>Déterministe:</strong> ${automate.type === 'AFD' ? 'Oui' : 'Non'}</li>
                </ul>
            </div>
            <div class="info-card">
                <h3>États</h3>
                <ul>
                    <li><strong>Initial:</strong> ${automate.etat_initial}</li>
                    <li><strong>Finaux:</strong> {${automate.etats_final.join(', ')}}</li>
                    <li><strong>Tous:</strong> {${automate.etats.join(', ')}}</li>
                </ul>
            </div>
            <div class="info-card">
                <h3>Transitions</h3>
                <ul>
                    ${Object.entries(automate.transitions).map(([etat, trans]) => 
                        Object.entries(trans).map(([symbole, dest]) => 
                            `<li>${etat} --${symbole}--> ${Array.isArray(dest) ? dest.join(', ') : dest}</li>`
                        ).join('')
                    ).join('')}
                </ul>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            <button class="button warning" onclick="canonizeAutomate()">🔧 Canoniser l'Automate</button>
        </div>
    `;
}

function updateAFDInfo(afd) {
    const afdDiv = document.getElementById('afdInfo');
    afdDiv.innerHTML = `
        <div class="automate-info">
            <div class="info-card">
                <h3>AFD Généré</h3>
                <ul>
                    <li><strong>États:</strong> ${afd.etats.length}</li>
                    <li><strong>État initial:</strong> ${afd.etat_initial}</li>
                    <li><strong>États finaux:</strong> {${afd.etats_final.join(', ')}}</li>
                </ul>
            </div>
            <div class="info-card">
                <h3>Transitions AFD</h3>
                <ul>
                    ${Object.entries(afd.transitions).map(([etat, trans]) => 
                        Object.entries(trans).map(([symbole, dest]) => 
                            `<li>${etat} --${symbole}--> ${dest}</li>`
                        ).join('')
                    ).join('')}
                </ul>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            <button class="button" onclick="showAFD()">👁️ Visualiser l'AFD</button>
            <button class="button warning" onclick="useAFD()">🔄 Utiliser cet AFD</button>
        </div>
    `;
}

function showAFD() {
    if (currentAFD) {
        drawAutomate(currentAFD);
        showMessage('Affichage de l\'AFD généré', 'info');
    }
}

function useAFD() {
    if (currentAFD) {
        currentAutomate = currentAFD;
        updateAutomateInfo(currentAutomate);
        drawAutomate(currentAutomate);
        
        // Mettre à jour les champs
        document.getElementById('alphabet').value = currentAFD.alphabet.join(',');
        document.getElementById('etats').value = currentAFD.etats.join(',');
        document.getElementById('etatInitial').value = currentAFD.etat_initial;
        document.getElementById('etatsFinaux').value = currentAFD.etats_final.join(',');
        document.getElementById('transitions').value = JSON.stringify(currentAFD.transitions, null, 2);
        
        document.getElementById('convertBtn').disabled = true;
        showMessage('AFD maintenant utilisé comme automate principal', 'success');
    }
}

// Dessin de l'automate
function drawAutomate(automate) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!automate || !automate.etats) return;
    
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);
    
    // Calculer les positions des états
    const positions = calculateStatePositions(automate.etats);
    
    // Dessiner les transitions
    drawTransitions(automate, positions);
    
    // Dessiner les états
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
        
        // Cercle de l'état
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, stateRadius, 0, 2 * Math.PI);
        ctx.fillStyle = automate.etats_final.includes(etat) ? '#e0f2fe' : '#f8fafc';
        ctx.fill();
        ctx.strokeStyle = automate.etats_final.includes(etat) ? '#0277bd' : '#374151';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Double cercle pour les états finaux
        if (automate.etats_final.includes(etat)) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, stateRadius - 5, 0, 2 * Math.PI);
            ctx.stroke();
        }
        
        // Flèche pour l'état initial
        if (etat === automate.etat_initial) {
            drawInitialArrow(pos.x - stateRadius - 20, pos.y, pos.x - stateRadius, pos.y);
        }
        
        // Nom de l'état
        ctx.fillStyle = '#374151';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(etat, pos.x, pos.y);
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
                
                if (fromState === toState) {
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
    
    // Calculer les points de départ et d'arrivée
    const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
    const startX = fromPos.x + stateRadius * Math.cos(angle);
    const startY = fromPos.y + stateRadius * Math.sin(angle);
    const endX = toPos.x - stateRadius * Math.cos(angle);
    const endY = toPos.y - stateRadius * Math.sin(angle);
    
    // Dessiner la ligne
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Dessiner la flèche
    drawArrowHead(endX, endY, angle);
    
    // Dessiner le label
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    drawTransitionLabel(midX, midY, symbol);
}

function drawSelfLoop(pos, symbol) {
    const stateRadius = 30;
    const loopRadius = 20;
    
    // Dessiner la boucle
    ctx.beginPath();
    ctx.arc(pos.x, pos.y - stateRadius - loopRadius, loopRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Dessiner la flèche
    const arrowX = pos.x + loopRadius * 0.7;
    const arrowY = pos.y - stateRadius - loopRadius * 2;
    drawArrowHead(arrowX, arrowY, Math.PI / 2);
    
    // Dessiner le label
    const labelX = pos.x;
    const labelY = pos.y - stateRadius - loopRadius * 2 - 10;
    drawTransitionLabel(labelX, labelY, symbol);
}

function drawArrowHead(x, y, angle) {
    const arrowSize = 10;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-arrowSize, -arrowSize / 2);
    ctx.lineTo(-arrowSize, arrowSize / 2);
    ctx.closePath();
    ctx.fillStyle = '#374151';
    ctx.fill();
    
    ctx.restore();
}

function drawTransitionLabel(x, y, symbol) {
    ctx.save();
    ctx.fillStyle = '#374151';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Fond blanc pour la lisibilité
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - 15, y - 10, 30, 20);
    
    // Texte du symbole
    ctx.fillStyle = '#374151';
    ctx.fillText(symbol, x, y);
    
    ctx.restore();
}

function drawInitialArrow(startX, startY, endX, endY) {
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Dessiner la flèche
    drawArrowHead(endX, endY, 0);
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 5000);
}