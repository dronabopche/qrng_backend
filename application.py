from flask import Flask, jsonify, request
from flask_cors import CORS
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qrng_core import QuantumRNG  # CHANGED: removed lib.backend.
from qrng_visualization import QRNGVisualizer  # CHANGED: removed lib.backend.

application = Flask(__name__)  # CHANGED: app -> application
CORS(application)

# Initialize components
qrng = QuantumRNG()
visualizer = QRNGVisualizer()

@application.route('/')  # CHANGED: @app -> @application
def home():
    return jsonify({
        'message': 'Quantum Random Number Generator API',
        'version': '1.0',
        'endpoints': {
            '/api/generate/<method>': 'Generate random numbers using specified method',
            '/api/benchmark': 'Benchmark all methods',
            '/api/methods': 'Get available methods'
        }
    })

@application.route('/api/generate/<method>', methods=['POST'])  # CHANGED
def generate_random_numbers(method):
    try:
        data = request.get_json() or {}
        shots = data.get('shots', 1024)
        qubits = data.get('qubits', 1)
        
        if method == 'hadamard':
            result = qrng.hadamard_method(num_qubits=qubits, shots=shots)
        elif method == 'bell':
            result = qrng.bell_state_method(shots=shots)
        elif method == 'ghz':
            result = qrng.ghz_state_method(num_qubits=qubits, shots=shots)
        elif method == 'nist':
            result = qrng.nist_compliant_method(shots=shots)
        else:
            return jsonify({'error': 'Invalid method'}), 400
        
        # Check if method execution had errors
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Generate classical comparison
        max_val = 2 ** qubits
        classical_bits = [format(np.random.randint(0, max_val), f'0{qubits}b') 
                         for _ in range(shots)]
        
        # Create visualization
        fig = visualizer.plot_distribution_comparison(
            result.get('counts', {}), 
            classical_bits,
            f"{result['method']} Method"
        )
        
        # Convert plot to base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        response = {
            'method': result['method'],
            'random_bits': result.get('random_bits', []),
            'processed_bits': result.get('processed_bits', []),
            'entropy': result['entropy'],
            'classical_comparison': classical_bits,
            'visualization': f"data:image/png;base64,{plot_url}",
            'total_bits': len(result.get('random_bits', [])),
            'shots': shots
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application.route('/api/benchmark', methods=['POST'])  # CHANGED
def run_benchmark():
    try:
        data = request.get_json() or {}
        runs = data.get('runs', 100)
        
        results = qrng.benchmark_methods(runs=runs)
        
        # Create visualization
        fig = visualizer.plot_benchmark_results(results)
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        return jsonify({
            'benchmark_results': results,
            'visualization': f"data:image/png;base64,{plot_url}",
            'total_runs': runs
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application.route('/api/methods', methods=['GET'])  # CHANGED
def get_methods():
    methods = {
        'hadamard': {
            'name': 'Hadamard Method',
            'description': 'Uses Hadamard gates to create superposition states',
            'parameters': ['qubits', 'shots']
        },
        'bell': {
            'name': 'Bell State Method',
            'description': 'Uses entangled Bell states for correlated randomness',
            'parameters': ['shots']
        },
        'ghz': {
            'name': 'GHZ State Method',
            'description': 'Uses Greenberger-Horne-Zeilinger multi-qubit entanglement',
            'parameters': ['qubits', 'shots']
        },
        'nist': {
            'name': 'NIST Compliant Method',
            'description': 'Combines multiple quantum sources with post-processing',
            'parameters': ['shots']
        }
    }
    return jsonify(methods)

if __name__ == '__main__':
    print("Starting Quantum RNG API Server...")
    print("Available at: http://localhost:5000")
    application.run(debug=True, port=5000, host='0.0.0.0')  # CHANGED: app -> application
