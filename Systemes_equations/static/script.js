
// Variables globales
let currentAutomaton = {
    alphabet: '',
    states: [],
    initialStates: [],
    finalStates: [],
    transitions: {}
};

let currentEquations = {};

// Gestion des onglets
function showTab(tabName) {
    // Retirer la classe active de tous les onglets et contenus
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Ajouter la classe active à l'onglet cliqué et son contenu
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// Génération des états
function generateStates() {
    const alphabet = document.getElementById('alphabet').value.trim();
    const nbStates = parseInt(document.getElementById('nbStates').value);

    if (!alphabet || !nbStates) {
        showAlert('⚠️ Veuillez remplir l\'alphabet et le nombre d\'états', 'error');
        return;
    }

    currentAutomaton.alphabet = alphabet;
    currentAutomaton.states = Array.from({length: nbStates}, (_, i) => i);

    // Génération des boutons d'états
    generateStateButtons('initialStates', 'initial');
    generateStateButtons('finalStates', 'final');

    document.getElementById('statesSection').classList.remove('hidden');
}

function generateStateButtons(containerId, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    currentAutomaton.states.forEach(state => {
        const btn = document.createElement('div');
        btn.className = 'state-btn';
        btn.textContent = `q${state}`;
        btn.onclick = () => toggleState(btn, state, type);
        container.appendChild(btn);
    });
}

function toggleState(btn, state, type) {
    btn.classList.toggle('selected');
    
    const statesArray = type === 'initial' ? currentAutomaton.initialStates : currentAutomaton.finalStates;
    const index = statesArray.indexOf(state);
    
    if (index === -1) {
        statesArray.push(state);
    } else {
        statesArray.splice(index, 1);
    }
}

function showTransitions() {
    if (currentAutomaton.initialStates.length === 0) {
        showAlert('⚠️ Veuillez sélectionner au moins un état initial', 'error');
        return;
    }

    generateTransitionsGrid();
    document.getElementById('transitionsSection').classList.remove('hidden');
}

function generateTransitionsGrid() {
    const grid = document.getElementById('transitionsGrid');
    grid.innerHTML = '';

    currentAutomaton.states.forEach(fromState => {
        currentAutomaton.alphabet.split('').forEach(symbol => {
            currentAutomaton.states.forEach(toState => {
                const item = document.createElement('div');
                item.className = 'transition-item';
                item.innerHTML = `q${fromState} --${symbol}--> q${toState}`;
                
                const key = `${fromState}_${symbol}`;
                item.onclick = () => toggleTransition(item, key, toState);
                
                grid.appendChild(item);
            });
        });
    });
}

function toggleTransition(item, key, toState) {
    item.classList.toggle('active');
    
    if (!currentAutomaton.transitions[key]) {
        currentAutomaton.transitions[key] = [];
    }
    
    const index = currentAutomaton.transitions[key].indexOf(toState);
    if (index === -1) {
        currentAutomaton.transitions[key].push(toState);
    } else {
        currentAutomaton.transitions[key].splice(index, 1);
        if (currentAutomaton.transitions[key].length === 0) {
            delete currentAutomaton.transitions[key];
        }
    }
}

async function generateEquations() {
    showLoading('equationsDisplay');
    
    try {
        const response = await fetch('/generate_equations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentAutomaton)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentEquations = data.equations;
            displayEquations(data.equations, 'equationsDisplay');
            showAlert('✅ Équations générées avec succès!', 'success');
            showTab('equations');
        } else {
            showAlert('❌ Erreur: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('❌ Erreur de communication: ' + error.message, 'error');
    }
}

function displayEquations(equations, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<h4>Système d\'équations:</h4>';
    
    Object.entries(equations).forEach(([variable, expression]) => {
        const div = document.createElement('div');
        div.className = 'equation';
        div.innerHTML = `<strong>${variable}</strong> = ${formatExpression(expression)}`;
        container.appendChild(div);
    });
}

async function solveGeneratedEquations() {
    await solveEquations(currentEquations);
}

function addManualEquation() {
    const container = document.getElementById('manualEquations');
    const div = document.createElement('div');
    div.className = 'manual-equation-input';
    div.innerHTML = `
        <input type="text" placeholder="Variable (ex: X0)" class="var-input">
        <span>=</span>
        <input type="text" placeholder="Expression (ex: aX1 + bX2 + ε)" class="expr-input">
        <button class="btn btn-danger" onclick="removeEquation(this)">❌</button>
    `;
    container.appendChild(div);
}

function removeEquation(btn) {
    btn.parentElement.remove();
}

async function solveManualEquations() {
    const equations = {};
    const inputs = document.querySelectorAll('.manual-equation-input');
    
    inputs.forEach(input => {
        const varInput = input.querySelector('.var-input').value.trim();
        const exprInput = input.querySelector('.expr-input').value.trim();
        
        if (varInput && exprInput) {
            equations[varInput] = exprInput;
        }
    });
    
    if (Object.keys(equations).length === 0) {
        showAlert('⚠️ Veuillez entrer au moins une équation', 'error');
        return;
    }
    
    await solveEquations(equations);
}

async function solveEquations(equations) {
    showLoading('solutionsDisplay');
    
    try {
        const response = await fetch('/solve_equations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ equations })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySolutions(data.solutions, data.steps);
            showAlert('✅ Équations résolues avec succès!', 'success');
            showTab('solutions');
        } else {
            showAlert('❌ Erreur: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('❌ Erreur de communication: ' + error.message, 'error');
    }
}

function displaySolutions(solutions, steps) {
    const container = document.getElementById('solutionsDisplay');
    container.innerHTML = '';
    
    // Afficher les solutions finales avec un style plus attrayant
    const solutionsDiv = document.createElement('div');
    solutionsDiv.className = 'solutions-section';
    solutionsDiv.innerHTML = '<h4>🎯 Solutions finales:</h4>';
    
    Object.entries(solutions).forEach(([variable, solution]) => {
        const div = document.createElement('div');
        div.className = 'equation solution-final';
        div.innerHTML = `<strong>${variable}</strong> = <span class="solution-text">${formatExpression(solution)}</span>`;
        solutionsDiv.appendChild(div);
    });
    
    container.appendChild(solutionsDiv);
    
    // Afficher les étapes de résolution détaillées
    if (steps && steps.length > 0) {
        const stepsDiv = document.createElement('div');
        stepsDiv.className = 'steps-container';
        stepsDiv.innerHTML = '<h4>📋 Étapes de résolution:</h4>';
        
        steps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-detailed';
            
            let stepContent = '';
            
            // Formatage détaillé selon le type d'étape
            if (step.method === "Lemme d'Arden") {
                stepContent = `
                    <div class="step-header">
                        <span class="step-number">Étape ${step.step || index + 1}</span>
                        <span class="step-method">${step.method}</span>
                    </div>
                    <div class="step-content">
                        <div class="step-equation">
                            <strong>${step.variable}</strong> = ${formatExpression(step.equation)}
                        </div>
                        <div class="step-arrow">↓</div>
                        <div class="step-result">
                            <strong>${step.variable}</strong> = <span class="highlight">${formatExpression(step.solution)}</span>
                        </div>
                        <div class="step-explanation">
                            Application du lemme d'Arden : X = AX + B ⇒ X = A*B
                        </div>
                    </div>
                `;
            } else if (step.method === "Substitution") {
                stepContent = `
                    <div class="step-header">
                        <span class="step-number">Étape ${step.step || index + 1}</span>
                        <span class="step-method">${step.method}</span>
                    </div>
                    <div class="step-content">
                        <div class="step-description">${step.description || 'Substitution dans les équations restantes'}</div>
                        <div class="step-equation">
                            <strong>${step.variable}</strong> = ${formatExpression(step.equation)}
                        </div>
                        <div class="step-arrow">↓</div>
                        <div class="step-result">
                            <strong>${step.variable}</strong> = <span class="highlight">${formatExpression(step.solution)}</span>
                        </div>
                    </div>
                `;
            } else if (step.method === "Regroupement") {
                stepContent = `
                    <div class="step-header">
                        <span class="step-number">Étape intermédiaire</span>
                        <span class="step-method">${step.method}</span>
                    </div>
                    <div class="step-content">
                        <div class="step-description">Regroupement des termes similaires</div>
                        <div class="step-equation">
                            ${formatExpression(step.equation)}
                        </div>
                        <div class="step-arrow">↓</div>
                        <div class="step-result">
                            <span class="highlight">${formatExpression(step.solution)}</span>
                        </div>
                    </div>
                `;
            } else {
                // Format par défaut
                stepContent = `
                    <div class="step-header">
                        <span class="step-number">Étape ${step.step || index + 1}</span>
                        <span class="step-method">${step.method}</span>
                    </div>
                    <div class="step-content">
                        <div class="step-equation">
                            <strong>${step.variable}</strong> = ${formatExpression(step.equation)}
                        </div>
                        <div class="step-arrow">↓</div>
                        <div class="step-result">
                            <strong>${step.variable}</strong> = <span class="highlight">${formatExpression(step.solution)}</span>
                        </div>
                    </div>
                `;
            }
            
            stepDiv.innerHTML = stepContent;
            stepsDiv.appendChild(stepDiv);
        });
        
        container.appendChild(stepsDiv);
    }
    
    // Ajouter un résumé final
    const resumeDiv = document.createElement('div');
    resumeDiv.className = 'resume-section';
    resumeDiv.innerHTML = `
        <h4>📊 Résumé de la résolution:</h4>
        <div class="resume-content">
            <p><strong>Nombre d'étapes:</strong> ${steps ? steps.length : 0}</p>
            <p><strong>Méthode principale:</strong> Lemme d'Arden avec substitutions successives</p>
            <p><strong>Variables résolues:</strong> ${Object.keys(solutions).join(', ')}</p>
        </div>
    `;
    container.appendChild(resumeDiv);
}

function resetAutomaton() {
    currentAutomaton = {
        alphabet: '',
        states: [],
        initialStates: [],
        finalStates: [],
        transitions: {}
    };
    currentEquations = {};
    
    document.getElementById('alphabet').value = '';
    document.getElementById('nbStates').value = '';
    document.getElementById('statesSection').classList.add('hidden');
    document.getElementById('transitionsSection').classList.add('hidden');
    document.getElementById('equationsDisplay').innerHTML = '<p>Créez d\'abord un automate pour voir les équations générées.</p>';
    
    showAlert('🔄 Automate réinitialisé', 'success');
    showTab('creation');
}

function showAlert(message, type) {
    // Retirer les anciennes alertes
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insérer l'alerte au début du contenu actuel
    const activeContent = document.querySelector('.tab-content.active');
    activeContent.insertBefore(alert, activeContent.firstChild);
    
    // Retirer l'alerte après 5 secondes
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Traitement en cours...</p>
        </div>
    `;
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter une équation manuelle par défaut
    addManualEquation();
    
    // Exemples d'équations prédéfinies
    const exampleBtn = document.createElement('button');
    exampleBtn.className = 'btn';
    exampleBtn.textContent = '📝 Charger exemple';
    exampleBtn.onclick = loadExample;
    
    const manualSection = document.querySelector('#manual .form-section');
    manualSection.appendChild(exampleBtn);
});

function loadExample() {
    // Charger l'exemple du document avec vos équations corrigées
    const container = document.getElementById('manualEquations');
    container.innerHTML = '';
    
    const examples = [
        { var: 'X1', expr: 'bX1 + aX2' },
        { var: 'X2', expr: 'bX1 + aX2 + bX3 + ε' },
        { var: 'X3', expr: 'bX1' }
    ];
    
    examples.forEach(example => {
        const div = document.createElement('div');
        div.className = 'manual-equation-input';
        div.innerHTML = `
            <input type="text" placeholder="Variable (ex: X0)" class="var-input" value="${example.var}">
            <span>=</span>
            <input type="text" placeholder="Expression (ex: aX1 + bX2 + ε)" class="expr-input" value="${example.expr}">
            <button class="btn btn-danger" onclick="removeEquation(this)">❌</button>
        `;
        container.appendChild(div);
    });
    
    showAlert('📝 Exemple chargé avec succès!', 'success');
}

// Validation des entrées
function validateAlphabet(alphabet) {
    return /^[a-zA-Z0-9]+$/.test(alphabet);
}

function validateEquation(variable, expression) {
    // Validation basique de la syntaxe
    const validPattern = /^[a-zA-Z0-9+\s\*\(\)ε]+$/;
    return validPattern.test(variable) && validPattern.test(expression);
}

// Gestion des raccourcis clavier
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                showTab('creation');
                break;
            case '2':
                e.preventDefault();
                showTab('equations');
                break;
            case '3':
                e.preventDefault();
                showTab('manual');
                break;
            case '4':
                e.preventDefault();
                showTab('solutions');
                break;
        }
    }
});

// Fonctions utilitaires pour l'affichage amélioré
function formatExpression(expr) {
    if (!expr) return '';
    
    // Remplacer les symboles pour un meilleur affichage
    return expr
        .replace(/\*/g, '<sup>*</sup>')
        .replace(/ε/g, '<span class="epsilon">ε</span>')
        .replace(/\+/g, ' + ')
        .replace(/\s+/g, ' ')
        .trim();
}

function exportSolutions() {
    const solutions = document.getElementById('solutionsDisplay').innerHTML;
    const fullHtml = `
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Solutions - Automate</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .solution-final { background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; }
                .step-detailed { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .step-header { background: #f0f0f0; padding: 8px; margin: -15px -15px 10px -15px; border-radius: 5px 5px 0 0; }
                .highlight { color: #007bff; font-weight: bold; }
                .epsilon { color: #28a745; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Solutions du système d'équations</h1>
            ${solutions}
        </body>
        </html>
    `;
    
    const blob = new Blob([fullHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'solutions_automate.html';
    a.click();
    URL.revokeObjectURL(url);
}

// Ajouter le bouton d'export dans l'onglet solutions
window.addEventListener('load', function() {
    const solutionsSection = document.querySelector('#solutions .form-section');
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn';
    exportBtn.textContent = '💾 Exporter les solutions';
    exportBtn.onclick = exportSolutions;
    solutionsSection.appendChild(exportBtn);
});

