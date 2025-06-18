// Variables globales
let currentAutomaton = {
    alphabet: '',
    states: [],
    initialStates: [],
    finalStates: [],
    transitions: {},
    testWords: []
};

        let currentStep = 1;

        // Gestion des onglets
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        // Génération des états
        function generateStates() {
            const alphabet = document.getElementById('alphabet').value.trim();
            const nbStates = parseInt(document.getElementById('nbStates').value);

            if (!alphabet || !nbStates) {
                alert('⚠️ Veuillez remplir l\'alphabet et le nombre d\'états');
                return;
            }

            currentAutomaton.alphabet = alphabet;
            currentAutomaton.states = Array.from({length: nbStates}, (_, i) => i);

            // Génération des boutons d'états
            generateStateButtons('initialStates', 'initial');
            generateStateButtons('finalStates', 'final');

            document.getElementById('statesSection').style.display = 'block';
            updateStep(2);
        }

        function generateStateButtons(containerId, type) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            currentAutomaton.states.forEach(state => {
                const button = document.createElement('div');
                button.className = 'state-tag';
                button.style.cursor = 'pointer';
                button.style.opacity = '0.6';
                button.innerHTML = `q${state} <span class="toggle">+</span>`;
                
                button.onclick = () => toggleState(state, type, button);
                container.appendChild(button);
            });
        }

        function toggleState(state, type, button) {
            const isSelected = button.style.opacity === '1';
            const targetArray = type === 'initial' ? currentAutomaton.initialStates : currentAutomaton.finalStates;

            if (isSelected) {
                // Retirer l'état
                const index = targetArray.indexOf(state);
                if (index > -1) targetArray.splice(index, 1);
                button.style.opacity = '0.6';
                button.querySelector('.toggle').textContent = '+';
            } else {
                // Ajouter l'état
                targetArray.push(state);
                button.style.opacity = '1';
                button.querySelector('.toggle').textContent = '✓';
            }
        }

        function nextStep() {
            if (currentAutomaton.initialStates.length === 0) {
                alert('⚠️ Veuillez sélectionner au moins un état initial');
                return;
            }
            if (currentAutomaton.finalStates.length === 0) {
                alert('⚠️ Veuillez sélectionner au moins un état final');
                return;
            }

            generateTransitionsGrid();
            showTab('transitions');
            updateStep(3);
        }

        function generateTransitionsGrid() {
            const grid = document.getElementById('transitionsGrid');
            grid.innerHTML = '';

            currentAutomaton.states.forEach(from => {
                currentAutomaton.alphabet.split('').forEach(symbol => {
                    currentAutomaton.states.forEach(to => {
                        const card = document.createElement('div');
                        card.className = 'transition-card';
                        card.innerHTML = `
                            <strong>q${from} --${symbol}--> q${to}</strong>
                        `;
                        card.onclick = () => toggleTransition(from, symbol, to, card);
                        grid.appendChild(card);
                    });
                });
            });
        }

        function toggleTransition(from, symbol, to, card) {
            const key = `${from}-${symbol}`;
            if (!currentAutomaton.transitions[key]) {
                currentAutomaton.transitions[key] = [];
            }

            const index = currentAutomaton.transitions[key].indexOf(to);
            if (index > -1) {
                currentAutomaton.transitions[key].splice(index, 1);
                card.classList.remove('selected');
            } else {
                currentAutomaton.transitions[key].push(to);
                card.classList.add('selected');
            }
        }

        async function saveAutomaton() {
            // Envoi des données au backend C
            try {
                const response = await fetch('/api/save-automaton', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(currentAutomaton)
                });

                if (response.ok) {
                    showAlert('✅ Automate enregistré avec succès!', 'success');
                    updateStep(4);
                    showTab('test');
                } else {
                    showAlert('❌ Erreur lors de l\'enregistrement', 'danger');
                }
            } catch (error) {
                showAlert('❌ Erreur de connexion au serveur', 'danger');
            }
        }

        function addTestWord() {
            const word = document.getElementById('testWord').value.trim();
            if (!word) return;

            if (!currentAutomaton.testWords.includes(word)) {
                currentAutomaton.testWords.push(word);
                updateTestList();
            }

            document.getElementById('testWord').value = '';
        }

        function updateTestList() {
            const container = document.getElementById('testItems');
            container.innerHTML = '';

            currentAutomaton.testWords.forEach((word, index) => {
                const item = document.createElement('div');
                item.className = 'test-item';
                item.innerHTML = `
                    <span><strong>"${word}"</strong></span>
                    <div>
                        <button class="btn" onclick="testSingleWord('${word}', ${index})">Tester</button>
                        <button class="btn btn-danger" onclick="removeTestWord(${index})">Supprimer</button>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        async function testSingleWord(word, index) {
            try {
                const response = await fetch('/api/test-word', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ word: word })
                });

                const result = await response.json();
                displayTestResult(word, result, index);
            } catch (error) {
                showAlert('❌ Erreur lors du test', 'danger');
            }
        }

        async function runAllTests() {
            document.getElementById('analysisResults').innerHTML = '<div class="loading"></div><p>Tests en cours...</p>';
            
            try {
                const response = await fetch('/api/test-all-words', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ words: currentAutomaton.testWords })
                });

                const results = await response.json();
                displayAllTestResults(results);
            } catch (error) {
                showAlert('❌ Erreur lors des tests', 'danger');
            }
        }

        async function analyzeAutomaton() {
            try {
                const response = await fetch('/api/analyze-automaton', {
                    method: 'GET'
                });

                const analysis = await response.json();
                displayAnalysis(analysis);
            } catch (error) {
                showAlert('❌ Erreur lors de l\'analyse', 'danger');
            }
        }

        function displayAnalysis(analysis) {
            const container = document.getElementById('analysisResults');
            let html = '<h4>📊 Résultats de l\'analyse</h4>';

            if (analysis.isDFA) {
                html += '<div class="alert alert-success">✅ Cet automate est un AFD (Automate Fini Déterministe)</div>';
            } else {
                html += '<div class="alert alert-warning">⚠️ Cet automate est un AFN (Automate Fini Non-déterministe)</div>';
                html += '<div class="alert alert-warning">';
                html += '<strong>Raisons:</strong><ul>';
                analysis.reasons.forEach(reason => {
                    html += `<li>${reason}</li>`;
                });
                html += '</ul></div>';
                html += '<button class="btn btn-success" onclick="determinizeNFA()">🔄 Déterminiser automatiquement</button>';
            }

            container.innerHTML = html;
        }

        async function determinizeNFA() {
            try {
                const response = await fetch('/api/determinize', {
                    method: 'POST'
                });

                const result = await response.json();
                
                if (result.success) {
                    showAlert('✅ AFN déterminisé avec succès!', 'success');
                    // Mettre à jour l'automate courant avec la version déterminisée
                    currentAutomaton = result.determinizedAutomaton;
                    regenerateInterface();
                } else {
                    showAlert('❌ Erreur lors de la déterminisation', 'danger');
                }
            } catch (error) {
                showAlert('❌ Erreur de connexion', 'danger');
            }
        }

        function displayTestResult(word, result, index) {
            const item = document.querySelectorAll('.test-item')[index];
            const resultDiv = item.querySelector('.result') || document.createElement('div');
            resultDiv.className = 'result';
            
            if (result.accepted) {
                resultDiv.innerHTML = `<span style="color: green;">✅ Accepté</span>`;
            } else {
                resultDiv.innerHTML = `<span style="color: red;">❌ Rejeté</span>`;
            }
            
            if (!item.querySelector('.result')) {
                item.appendChild(resultDiv);
            }
        }

        function removeTestWord(index) {
            currentAutomaton.testWords.splice(index, 1);
            updateTestList();
        }

        function showAlert(message, type) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.textContent = message;
            
            document.querySelector('.container').prepend(alertDiv);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }

        function updateStep(step) {
            document.querySelectorAll('.step').forEach((s, i) => {
                s.classList.remove('active', 'completed');
                if (i + 1 < step) s.classList.add('completed');
                else if (i + 1 === step) s.classList.add('active');
            });
            currentStep = step;
        }

        function visualizeAutomaton() {
            const viz = document.getElementById('visualization');
            viz.innerHTML = `
                <div class="loading"></div>
                <p>Génération de la visualisation...</p>
            `;
            
            // Simuler la génération d'une visualisation
            setTimeout(() => {
                viz.innerHTML = `
                    <h4>🎨 Visualisation de l'automate</h4>
                    <p>États: ${currentAutomaton.states.length}</p>
                    <p>États initiaux: ${currentAutomaton.initialStates.join(', ')}</p>
                    <p>États finaux: ${currentAutomaton.finalStates.join(', ')}</p>
                    <p>Alphabet: ${currentAutomaton.alphabet}</p>
                    <p>Transitions: ${Object.keys(currentAutomaton.transitions).length}</p>
                `;
            }, 2000);
        }

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            updateStep(1);
        });

