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

document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('automateCanvas');
    ctx = canvas.getContext('2d');

    resizeCanvas();
    canvas.addEventListener('wheel', handleWheel);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);
    window.addEventListener('resize', resizeCanvas);

    loadExample('complex');
});

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

async function createAutomate() {
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

        const automateData = {
            alphabet,
            etats,
            transitions,
            etat_initial: etatInitial,
            etats_final: etatsFinaux
        };

        const response = await fetch('http://localhost:5000/api/automate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(automateData)
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        currentAutomate = result.automate;
        document.getElementById('convertBtn').disabled = currentAutomate.type === 'AFD';
        document.getElementById('testBtn').disabled = false;
        updateAutomateInfo(currentAutomate);
        drawAutomate(currentAutomate);
        showMessage(result.message, 'success');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

async function convertToAFD() {
    if (!currentAutomate) {
        showMessage('Aucun automate à convertir', 'warning');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentAutomate)
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        currentAFD = result.afd;
        document.getElementById('afdPanel').style.display = 'block';
        updateAFDInfo(currentAFD);
        showMessage(result.message, 'success');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

async function canonizeAutomate() {
    if (!currentAutomate) {
        showMessage('Aucun automate à canoniser', 'warning');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/canonize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentAutomate)
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        currentAutomate = result.automate;
        document.getElementById('alphabet').value = currentAutomate.alphabet.join(',');
        document.getElementById('etats').value = currentAutomate.etats.join(',');
        document.getElementById('etatInitial').value = currentAutomate.etat_initial;
        document.getElementById('etatsFinaux').value = currentAutomate.etats_final.join(',');
        document.getElementById('transitions').value = JSON.stringify(currentAutomate.transitions, null, 2);
        document.getElementById('convertBtn').disabled = currentAutomate.type === 'AFD';
        document.getElementById('testBtn').disabled = false;
        updateAutomateInfo(currentAutomate);
        drawAutomate(currentAutomate);
        showMessage(result.message, 'success');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

async function testWord() {
    const word = document.getElementById('testWord').value.trim();
    if (!currentAutomate) {
        showMessage('Aucun automate créé', 'warning');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...currentAutomate, mot: word })
        });

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        displayTestResult(result, word);
        showMessage(result.message, result.accepte ? 'success' : 'error');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

async function validateAutomate() {
    if (!currentAutomate) {
        showMessage('Aucun automate à valider', 'warning');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentAutomate)
        });

        const result = await response.json();
        if (!result.success) {
            showMessage('Erreurs trouvées: ' + result.errors.join(', '), 'error');
            return;
        }

        let message = 'Automate valide ✅';
        if (result.warnings.length > 0) {
            message += '<br>Avertissements: ' + result.warnings.join(', ');
        }
        showMessage(message, 'success');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

async function loadExample(type) {
    try {
        const response = await fetch('http://localhost:5000/api/examples');
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        const example = result.examples[type];
        if (!example) {
            throw new Error('Exemple non trouvé');
        }

        document.getElementById('alphabet').value = example.alphabet.join(',');
        document.getElementById('etats').value = example.etats.join(',');
        document.getElementById('etatInitial').value = example.etat_initial;
        document.getElementById('etatsFinaux').value = example.etats_final.join(',');
        document.getElementById('transitions').value = JSON.stringify(example.transitions, null, 2);

        await createAutomate();
    } catch (error) {
        showMessage('Erreur lors du chargement de l\'exemple: ' + error.message, 'error');
    }
}

function clearForm() {
    document.getElementById('alphabet').value = '';
    document.getElementById('etats').value = '';
    document.getElementById('etatInitial').value = '';
    document.getElementById('etatsFinaux').value = '';
    document.getElementById('transitions').value = '';
    document.getElementById('testWord').value = '';
    document.getElementById('testResult').innerHTML = '';
    document.getElementById('afdPanel').style.display = 'none';
    document.getElementById('automateInfo').innerHTML = '<h2>📋 Informations de l\'Automate</h2><p>Créez un automate pour voir les informations ici.</p>';
    currentAutomate = null;
    currentAFD = null;
    document.getElementById('convertBtn').disabled = true;
    document.getElementById('testBtn').disabled = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    showMessage('Formulaire effacé', 'info');
}

function exportCanvas() {
    if (!currentAutomate) {
        showMessage('Aucun automate à exporter', 'warning');
        return;
    }
    const link = document.createElement('a');
    link.download = 'automate.png';
    link.href = canvas.toDataURL();
    link.click();
    showMessage('Image exportée', 'success');
}

function parseInput(input) {
    return input.split(',').map(s => s.trim()).filter(s => s.length > 0);
}

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
        document.getElementById('alphabet').value = currentAFD.alphabet.join(',');
        document.getElementById('etats').value = currentAFD.etats.join(',');
        document.getElementById('etatInitial').value = currentAFD.etat_initial;
        document.getElementById('etatsFinaux').value = currentAFD.etats_final.join(',');
        document.getElementById('transitions').value = JSON.stringify(currentAFD.transitions, null, 2);
        document.getElementById('convertBtn').disabled = true;
        showMessage('AFD maintenant utilisé comme automate compromise', 'success');
    }
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
        ctx.fillStyle = automate.etats_final.includes(etat) ? '#e0f2fe' : '#f8fafc';
        ctx.fill();
        ctx.strokeStyle = automate.etats_final.includes(etat) ? '#0277bd' : '#374151';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (automate.etats_final.includes(etat)) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, stateRadius - 5, 0, 2 * Math.PI);
            ctx.stroke();
        }

        if (etat === automate.etat_initial) {
            drawInitialArrow(pos.x - stateRadius - 20, pos.y, pos.x - stateRadius, pos.y);
        }

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
    const loopRadius = 20;

    ctx.beginPath();
    ctx.arc(pos.x, pos.y - stateRadius - loopRadius, loopRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 2;
    ctx.stroke();

    const arrowX = pos.x + loopRadius * 0.7;
    const arrowY = pos.y - stateRadius - loopRadius * 2;
    drawArrowHead(arrowX, arrowY, Math.PI / 2);

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
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - 15, y - 10, 30, 20);
    ctx.fillStyle = '#374151';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
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
    drawArrowHead(endX, endY, 0);
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

function showMessage(message, type) {
    const messageDiv = document.getElementById('messages');
    messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 5000);
}