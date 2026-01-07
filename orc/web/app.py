"""
ORC Web: Flask Application
"""
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys

# Add the project root to the path so we can import ORC modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from orc_package.config.settings import load_config
from storage.graph_db import GraphStorage
from core.analyzer import Analyzer
from agent.recommender import Recommender
from core.index_service import IndexService
from analysis.complexity import ComplexityAnalyzer
from analysis.optimizer import Optimizer

app = Flask(__name__)

# Load configuration
config = load_config()
storage = GraphStorage(config.index_path)
index_service = IndexService(config)

@app.route('/')
def dashboard():
    """Main dashboard showing codebase overview"""
    try:
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')

        # Get analysis summary
        analyzer = Analyzer(config)
        report = analyzer.run_all(modules)
        summary = report.get('summary', {})

        # Get complexity analysis
        complexity_analyzer = ComplexityAnalyzer({}, graph)
        complexity_report = complexity_analyzer.analyze_all()

        # Get optimization suggestions
        optimizer = Optimizer()

        return render_template('dashboard.html',
                             summary=summary,
                             total_files=summary.get('total_files', 0),
                             total_functions=summary.get('total_functions', 0),
                             total_lines=summary.get('total_lines', 0),
                             complexity_report=complexity_report[:10],  # Top 10 complex functions
                             total_complex_functions=len(complexity_report))
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/graph')
def graph_view():
    """Dependency graph visualization"""
    try:
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')

        # Prepare graph data for frontend
        if graph:
            nodes = []
            edges = []

            # Add nodes
            for node in graph.module_graph.nodes():
                node_data = graph.module_graph.nodes[node]
                nodes.append({
                    'id': node,
                    'label': Path(node).name,
                    'size': node_data.get('functions', 1) * 5,
                    'color': '#3498db' if node_data.get('functions', 0) > 5 else '#2ecc71',
                    'title': f'{Path(node).name}<br/>Functions: {node_data.get("functions", 0)}<br/>Lines: {node_data.get("lines", 0)}'
                })

            # Add edges
            for edge in graph.module_graph.edges():
                edges.append({
                    'from': edge[0],
                    'to': edge[1]
                })

            return render_template('graph.html', nodes=nodes, edges=edges)
        else:
            return render_template('graph.html', nodes=[], edges=[])
    except Exception as e:
        return f"Error loading graph: {str(e)}", 500

@app.route('/complexity')
def complexity_view():
    """Complexity analysis visualization"""
    try:
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')

        # Create complexity analyzer with current index
        index = index_service._get_current_index()
        complexity_analyzer = ComplexityAnalyzer(index, graph)
        complexity_report = complexity_analyzer.get_complex_functions(threshold=10)

        # Prepare data for visualization
        complexity_data = []
        for report in complexity_report:
            complexity_data.append({
                'function': report.function,
                'file': report.file,
                'time_complexity': report.time_complexity,
                'space_complexity': report.space_complexity,
                'complexity_score': report.complexity_score,
                'suggestion': report.suggestion
            })

        return render_template('complexity.html',
                             complexity_data=complexity_data,
                             total_complex_functions=len(complexity_data))
    except Exception as e:
        return f"Error loading complexity view: {str(e)}", 500

@app.route('/recommendations')
def recommendations_view():
    """Recommendations page"""
    try:
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')

        if modules and graph:
            recommender = Recommender(config, modules, graph)
            recommendations = recommender.generate_recommendations()

            # Convert to dict for template
            rec_dicts = [rec.to_dict() for rec in recommendations[:20]]  # Limit to 20

            return render_template('recommendations.html',
                                 recommendations=rec_dicts,
                                 total_recommendations=len(recommendations))
        else:
            return render_template('recommendations.html',
                                 recommendations=[],
                                 total_recommendations=0)
    except Exception as e:
        return f"Error loading recommendations: {str(e)}", 500

@app.route('/api/search')
def search():
    """API endpoint for searching codebase"""
    query = request.args.get('q', '')

    try:
        modules = storage.load_modules()

        # Simple search implementation
        results = []
        for path, module in modules.items():
            if query.lower() in path.lower():
                results.append({
                    'type': 'file',
                    'name': Path(path).name,
                    'path': path,
                    'lines': module.lines
                })

            # Search in function names
            for func_name in module.functions.keys():
                if query.lower() in func_name.lower():
                    results.append({
                        'type': 'function',
                        'name': func_name,
                        'file': Path(path).name,
                        'path': f"{path}::{func_name}"
                    })

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze')
def api_analyze():
    """API endpoint for getting analysis data"""
    try:
        modules = storage.load_modules()
        analyzer = Analyzer(config)
        report = analyzer.run_all(modules)

        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complexity')
def api_complexity():
    """API endpoint for getting complexity analysis"""
    try:
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')

        # Create complexity analyzer with current index
        index = index_service._get_current_index()
        complexity_analyzer = ComplexityAnalyzer(index, graph)
        complexity_report = complexity_analyzer.analyze_all()

        # Convert to JSON serializable format
        complexity_data = []
        for report in complexity_report:
            complexity_data.append({
                'function': report.function,
                'file': report.file,
                'time_complexity': report.time_complexity,
                'space_complexity': report.space_complexity,
                'hotspot': report.hotspot,
                'suggestion': report.suggestion,
                'estimated_improvement': report.estimated_improvement,
                'complexity_score': report.complexity_score
            })

        return jsonify({
            'complexity_data': complexity_data,
            'total_functions': len(complexity_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)