import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import networkx as nx

class VisualizationService:
    """Service pour la visualisation des automates"""
    
    @staticmethod
    def generate_graph(automaton_data):
        """Générer un graphique pour un automate"""
        try:
            # Créer un graphe dirigé
            G = nx.DiGraph()
            
            # Ajouter les nœuds (états)
            for state in automaton_data.get('states', []):
                node_color = 'lightgreen' if state.get('initial') else 'lightblue'
                if state.get('final'):
                    node_color = 'lightcoral'
                
                G.add_node(state['name'], color=node_color)
            
            # Ajouter les arêtes (transitions)
            edge_labels = {}
            for transition in automaton_data.get('transitions', []):
                from_state = transition['from']
                to_state = transition['to']
                symbol = transition['symbol']
                
                if G.has_edge(from_state, to_state):
                    # Combiner les symboles pour les transitions multiples
                    current_label = edge_labels.get((from_state, to_state), "")
                    edge_labels[(from_state, to_state)] = f"{current_label},{symbol}" if current_label else symbol
                else:
                    G.add_edge(from_state, to_state)
                    edge_labels[(from_state, to_state)] = symbol
            
            # Créer la visualisation
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Dessiner les nœuds
            node_colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000)
            
            # Dessiner les arêtes
            nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
            
            # Ajouter les labels des nœuds
            nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
            
            # Ajouter les labels des arêtes
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10)
            
            plt.title(f"Automate: {automaton_data.get('name', 'Sans nom')}")
            plt.axis('off')
            
            # Convertir en image base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'success': True,
                'image': f"data:image/png;base64,{image_base64}",
                'graph_data': {
                    'nodes': list(G.nodes()),
                    'edges': list(G.edges()),
                    'node_count': len(G.nodes()),
                    'edge_count': len(G.edges())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def compare_automata(automaton1_data, automaton2_data):
        """Comparer deux automates visuellement"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
            
            # Générer les graphiques pour chaque automate
            for i, (automaton_data, ax) in enumerate([(automaton1_data, ax1), (automaton2_data, ax2)]):
                G = nx.DiGraph()
                
                # Construction du graphe (même logique que generate_graph)
                for state in automaton_data.get('states', []):
                    node_color = 'lightgreen' if state.get('initial') else 'lightblue'
                    if state.get('final'):
                        node_color = 'lightcoral'
                    G.add_node(state['name'], color=node_color)
                
                edge_labels = {}
                for transition in automaton_data.get('transitions', []):
                    from_state = transition['from']
                    to_state = transition['to']
                    symbol = transition['symbol']
                    
                    if G.has_edge(from_state, to_state):
                        current_label = edge_labels.get((from_state, to_state), "")
                        edge_labels[(from_state, to_state)] = f"{current_label},{symbol}" if current_label else symbol
                    else:
                        G.add_edge(from_state, to_state)
                        edge_labels[(from_state, to_state)] = symbol
                
                # Dessiner sur le subplot approprié
                pos = nx.spring_layout(G, k=2, iterations=50)
                node_colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
                
                nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, ax=ax)
                nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=ax)
                nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)
                nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10, ax=ax)
                
                ax.set_title(f"Automate {i+1}: {automaton_data.get('name', 'Sans nom')}")
                ax.axis('off')
            
            plt.tight_layout()
            
            # Convertir en image base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'success': True,
                'comparison_image': f"data:image/png;base64,{image_base64}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_step_by_step(algorithm, data):
        """Générer une visualisation étape par étape"""
        # TODO: Implémenter la visualisation étape par étape
        return {
            'success': True,
            'steps': [],
            'message': 'Visualisation étape par étape en cours de développement'
        }
