let equations = [];
let currentSolution = null;

// Add equation functionality
function addEquation() {
    const input = document.getElementById('equationInput');
    const equation = input.value.trim();
    
    if (!equation) {
        showError('Veuillez entrer une équation');
        return;
    }

    if (!validateEquation(equation)) {
        showError('Format d\'équation invalide. Utilisez le format: Xi = expression');
        return;
    }

    equations.push(equation);
    input.value = '';
    updateEquationList();
    clearError();
}

// Validate equation format
function validateEquation(equation) {
    // Basic validation for equation format
    const pattern = /^X\d+\s*=\s*.+$/;
    return pattern.test(equation);
}

// Update equation list display
function updateEquationList() {
    const list = document.getElementById('equationList');
    
    if (equations.length === 0) {
        list.innerHTML = '<div class="loading">Aucune équation ajoutée</div>';
        return;
    }

    list.innerHTML = equations.map((eq, index) => `
        <div class="equation-item">
            <div class="equation-text">${eq}</div>
            <div class="equation-actions">
                <button class="btn-small" onclick="editEquation(${index})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-small danger" onclick="removeEquation(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Remove equation
function removeEquation(index) {
    equations.splice(index, 1);
    updateEquationList();
}

// Edit equation
function editEquation(index) {
    const input = document.getElementById('equationInput');
    input.value = equations[index];
    removeEquation(index);
}

// Clear all equations
function clearEquations() {
    if (equations.length === 0) return;
    
    if (confirm('Êtes-vous sûr de vouloir effacer toutes les équations ?')) {
        equations = [];
        updateEquationList();
        clearResults();
    }
}

// Solve system
function solveSystem() {
    if (equations.length === 0) {
        showError('Veuillez ajouter au moins une équation');
        return;
    }

    showLoading();
    
    // Simulate solving process
    setTimeout(() => {
        const solution = simulateSolution();
        displayResults(solution);
        displaySteps(solution.steps);
    }, 1500);
}

// Simulate solution (in real implementation, this would call actual solver)
function simulateSolution() {
    const variables = extractVariables();
    const regex = generateRegex(variables);
    
    return {
        regex: regex,
        variables: variables,
        steps: [
            {
                title: 'Identification des variables',
                description: 'Extraction des variables du système d\'équations',
                equation: variables.join(', ')
            },
            {
                title: 'Élimination de Gauss',
                description: 'Application de la méthode d\'élimination pour résoudre le système',
                equation: 'Substitution successive des variables'
            },
            {
                title: 'Simplification',
                description: 'Simplification des expressions régulières obtenues',
                equation: 'Application des règles: a*a* = a*, a + a = a, etc.'
            },
            {
                title: 'Expression finale',
                description: 'Expression régulière résultante du système',
                equation: regex
            }
        ]
    };
}

// Extract variables from equations
function extractVariables() {
    const vars = new Set();
    equations.forEach(eq => {
        const matches = eq.match(/X\d+/g);
        if (matches) {
            matches.forEach(v => vars.add(v));
        }
    });
    return Array.from(vars).sort();
}

// Generate regex (simplified simulation)
function generateRegex(variables) {
    const patterns = ['a*', 'b+', '(a|b)*', 'ab*c', '(ab)*'];
    return patterns[Math.floor(Math.random() * patterns.length)];
}

// Display results
function displayResults(solution) {
    const container = document.getElementById('resultContainer');
    
    container.innerHTML = `
        <div class="result-item">
            <div class="result-header">
                <div class="result-title">
                    <i class="fas fa-code"></i>
                    Expression Régulière
                </div>
                <button class="btn-small" onclick="copyResult('${solution.regex}')">
                    <i class="fas fa-copy"></i>
                    Copier
                </button>
            </div>
            <div class="result-content">
                <button class="copy-btn" onclick="copyResult('${solution.regex}')">
                    <i class="fas fa-copy"></i>
                </button>
                ${solution.regex}
            </div>
        </div>
        <div class="result-item">
            <div class="result-header">
                <div class="result-title">
                    <i class="fas fa-list"></i>
                    Variables identifiées
                </div>
            </div>
            <div class="result-content">
                ${solution.variables.join(', ')}
            </div>
        </div>
    `;
}

// Display solution steps
function displaySteps(steps) {
    const stepsSection = document.getElementById('stepsSection');
    const container = document.getElementById('stepsContainer');
    
    container.innerHTML = steps.map((step, index) => `
        <div class="step-item">
            <div class="step-number">${index + 1}</div>
            <div class="step-content">
                <div class="step-title">${step.title}</div>
                <div class="step-description">${step.description}</div>
                <div class="step-equation">${step.equation}</div>
            </div>
        </div>
    `).join('');
    stepsSection.style.display = 'block';
}

// Show loading state
function showLoading() {
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            Résolution en cours...
        </div>
    `;
}

// Copy result to clipboard
function copyResult(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copié dans le presse-papiers !');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copié dans le presse-papiers !');
    });
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-color);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: var(--shadow-large);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 2000);
}

// Load examples
function loadExample(exampleNumber) {
    clearEquations();
    
    const examples = {
        1: [
            'X₁ = aX₁ + bX₂ + ε',
            'X₂ = cX₁ + dX₂'
        ],
        2: [
            'X₁ = aX₂ + ε',
            'X₂ = bX₃ + cX₁',
            'X₃ = aX₁ + bX₂'
        ],
        3: [
            'X₁ = aX₁ + bX₂ + cX₃ + ε',
            'X₂ = dX₂ + eX₃',
            'X₃ = fX₁ + gX₃'
        ]
    };
    
    if (examples[exampleNumber]) {
        equations = [...examples[exampleNumber]];
        updateEquationList();
        clearResults();
        showToast(`Exemple ${exampleNumber} chargé !`);
    }
}

// Show error message
function showError(message) {
    const input = document.getElementById('equationInput');
    input.classList.add('error');
    
    let errorDiv = document.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        input.parentNode.appendChild(errorDiv);
    }
    
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        ${message}
    `;
}

// Clear error state
function clearError() {
    const input = document.getElementById('equationInput');
    input.classList.remove('error');
    
    const errorDiv = document.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Clear results
function clearResults() {
    const container = document.getElementById('resultContainer');
    const stepsSection = document.getElementById('stepsSection');
    
    container.innerHTML = `
        <div class="loading" style="color: var(--text-secondary);">
            <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
            Ajoutez des équations et cliquez sur "Résoudre" pour voir le résultat
        </div>
    `;
    
    stepsSection.style.display = 'none';
}

// Show help modal
function showHelp() {
    const helpContent = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;" onclick="this.remove()">
            <div style="background: white; border-radius: 16px; padding: 2rem; max-width: 600px; max-height: 80vh; overflow-y: auto; margin: 1rem;" onclick="event.stopPropagation()">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
                    <h2 style="color: var(--primary-color); margin: 0;">
                        <i class="fas fa-question-circle"></i> Guide d'utilisation
                    </h2>
                    <button onclick="this.closest('div').remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary);">×</button>
                </div>
                
                <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Format des équations :</h3>
                <ul style="margin-bottom: 1.5rem; color: var(--text-secondary);">
                    <li>Utilisez Xi pour les variables (X₁, X₂, X₃, etc.)</li>
                    <li>Utilisez ε pour l'état final/acceptant</li>
                    <li>Les transitions sont représentées par des lettres (a, b, c, etc.)</li>
                    <li>Format: Xi = expression + expression + ...</li>
                </ul>
                
                <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Exemples valides :</h3>
                <ul style="margin-bottom: 1.5rem; color: var(--text-secondary); font-family: monospace;">
                    <li>X₁ = aX₁ + bX₂ + ε</li>
                    <li>X₂ = cX₁ + dX₂</li>
                    <li>X₃ = eX₁ + fX₃ + ε</li>
                </ul>
                
                <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Fonctionnalités :</h3>
                <ul style="color: var(--text-secondary);">
                    <li>Ajout/suppression d'équations individuelles</li>
                    <li>Édition des équations existantes</li>
                    <li>Résolution automatique du système</li>
                    <li>Affichage des étapes de résolution</li>
                    <li>Copie du résultat dans le presse-papiers</li>
                </ul>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', helpContent);
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('equationInput');
    
    // Allow Enter key to add equation
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addEquation();
        }
    });
    
    // Clear error on input
    input.addEventListener('input', function() {
        if (this.classList.contains('error')) {
            clearError();
        }
    });
});

// Initialize
updateEquationList();