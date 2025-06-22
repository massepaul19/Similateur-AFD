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
                div.innerHTML = `<strong>${variable}</strong> = ${expression}`;
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
            
            // Afficher les solutions finales
            const solutionsDiv = document.createElement('div');
            solutionsDiv.innerHTML = '<h4>🎯 Solutions finales:</h4>';
            
            Object.entries(solutions).forEach(([variable, solution]) => {
                const div = document.createElement('div');
                div.className = 'equation solution';
                div.innerHTML = `<strong>${variable}</strong> = ${solution}`;
                solutionsDiv.appendChild(div);
            });
            
            container.appendChild(solutionsDiv);
            
            // Afficher les étapes de résolution
            if (steps && steps.length > 0) {
                const stepsDiv = document.createElement('div');
                stepsDiv.className = 'steps-container';
                stepsDiv.innerHTML = '<h4>📋 Étapes de résolution:</h4>';
                
                steps.forEach((step, index) => {
                    const stepDiv = document.createElement('div');
                    stepDiv.className = 'step';
                    stepDiv.innerHTML = `
                        <div class="step-title">Étape ${index + 1}: ${step.method}</div>
                        <div><strong>${step.variable}</strong> = ${step.equation}</div>
                        <div>→ <strong>${step.variable}</strong> = ${step.solution}</div>
                    `;
                    stepsDiv.appendChild(stepDiv);
                });
                
                container.appendChild(stepsDiv);
            }
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
            // Charger l'exemple du document
            const container = document.getElementById('manualEquations');
            container.innerHTML = '';
            
            const examples = [
                { var: 'X0', expr: 'bX0 + aX1' },
                { var: 'X1', expr: 'aX2 + bX3' },
                { var: 'X2', expr: 'aX1 + bX3 + ε' },
                { var: 'X3', expr: 'bX1 + aX3' }
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

        // Fonctions utilitaires pour l'affichage
        function formatExpression(expr) {
            // Remplacer les symboles pour un meilleur affichage
            return expr
                .replace(/\*/g, '*')
                .replace(/ε/g, 'ε')
                .replace(/\+/g, ' + ')
                .replace(/\s+/g, ' ')
                .trim();
        }

        function exportSolutions() {
            const solutions = document.getElementById('solutionsDisplay').innerHTML;
            const blob = new Blob([solutions], { type: 'text/html' });
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
