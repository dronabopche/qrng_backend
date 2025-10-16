import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import time
from typing import List, Dict
import json

class QuantumRNG:
    def __init__(self, backend=None):
        self.backend = backend or AerSimulator()
        self.results_cache = {}
    
    def hadamard_method(self, num_qubits: int = 1, shots: int = 1024) -> Dict:
        """Method 1: Hadamard gates on multiple qubits"""
        try:
            circuit = QuantumCircuit(num_qubits, num_qubits)
            
            # Apply Hadamard to create superposition
            for qubit in range(num_qubits):
                circuit.h(qubit)
            
            # Measure all qubits
            circuit.measure(range(num_qubits), range(num_qubits))
            
            # Execute
            compiled_circuit = transpile(circuit, self.backend)
            job = self.backend.run(compiled_circuit, shots=shots)
            result = job.result()
            counts = result.get_counts()
            
            # Convert to binary strings and extract randomness
            random_bits = []
            for binary_string, count in counts.items():
                random_bits.extend([binary_string] * count)
            
            return {
                'method': 'Hadamard',
                'circuit': circuit,
                'counts': counts,
                'random_bits': random_bits,
                'entropy': self._calculate_entropy(counts)
            }
        except Exception as e:
            return {'error': f'Hadamard method failed: {str(e)}'}
    
    def bell_state_method(self, shots: int = 1024) -> Dict:
        """Method 2: Bell State entanglement"""
        try:
            circuit = QuantumCircuit(2, 2)
            
            # Create Bell state
            circuit.h(0)
            circuit.cx(0, 1)
            circuit.measure([0, 1], [0, 1])
            
            compiled_circuit = transpile(circuit, self.backend)
            job = self.backend.run(compiled_circuit, shots=shots)
            result = job.result()
            counts = result.get_counts()
            
            random_bits = []
            for binary_string, count in counts.items():
                random_bits.extend([binary_string] * count)
            
            return {
                'method': 'Bell_State',
                'circuit': circuit,
                'counts': counts,
                'random_bits': random_bits,
                'entropy': self._calculate_entropy(counts)
            }
        except Exception as e:
            return {'error': f'Bell state method failed: {str(e)}'}
    
    def ghz_state_method(self, num_qubits: int = 3, shots: int = 1024) -> Dict:
        """Method 3: GHZ State entanglement"""
        try:
            circuit = QuantumCircuit(num_qubits, num_qubits)
            
            # Create GHZ state
            circuit.h(0)
            for i in range(1, num_qubits):
                circuit.cx(0, i)
            
            circuit.measure(range(num_qubits), range(num_qubits))
            
            compiled_circuit = transpile(circuit, self.backend)
            job = self.backend.run(compiled_circuit, shots=shots)
            result = job.result()
            counts = result.get_counts()
            
            random_bits = []
            for binary_string, count in counts.items():
                random_bits.extend([binary_string] * count)
            
            return {
                'method': 'GHZ_State',
                'circuit': circuit,
                'counts': counts,
                'random_bits': random_bits,
                'entropy': self._calculate_entropy(counts)
            }
        except Exception as e:
            return {'error': f'GHZ state method failed: {str(e)}'}
    
    def nist_compliant_method(self, shots: int = 1024) -> Dict:
        """Method 4: NIST SP 800-22 inspired method"""
        try:
            circuits = []
            all_bits = []
            
            # Generate from multiple quantum sources
            for i in range(4):
                circuit = QuantumCircuit(2, 2)
                circuit.h(0)
                circuit.h(1)
                circuit.rz(np.pi/4, 0)  # Additional rotation for diversity
                circuit.rz(np.pi/3, 1)
                circuit.measure([0, 1], [0, 1])
                
                compiled_circuit = transpile(circuit, self.backend)
                job = self.backend.run(compiled_circuit, shots=shots//4)
                result = job.result()
                counts = result.get_counts()
                
                circuits.append(circuit)
                for binary_string, count in counts.items():
                    all_bits.extend([binary_string] * count)
            
            # Apply NIST-inspired post-processing (Von Neumann extractor)
            processed_bits = self._von_neumann_extractor(all_bits)
            
            return {
                'method': 'NIST_Compliant',
                'circuits': circuits,
                'raw_bits': all_bits,
                'processed_bits': processed_bits,
                'entropy': self._calculate_bit_entropy(processed_bits)
            }
        except Exception as e:
            return {'error': f'NIST method failed: {str(e)}'}
    
    def _von_neumann_extractor(self, bits: List[str]) -> List[str]:
        """Von Neumann debiasing extractor"""
        output = []
        for bit_pair in bits:
            if len(bit_pair) == 2:
                if bit_pair == '01':
                    output.append('0')
                elif bit_pair == '10':
                    output.append('1')
        return output
    
    def _calculate_entropy(self, counts: Dict) -> float:
        """Calculate Shannon entropy of the distribution"""
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0
            
        entropy = 0.0
        for count in counts.values():
            probability = count / total_shots
            if probability > 0:
                entropy -= probability * np.log2(probability)
        return entropy
    
    def _calculate_bit_entropy(self, bits: List[str]) -> float:
        """Calculate entropy of bit sequence"""
        if not bits:
            return 0.0
        
        bit_string = ''.join(bits)
        counts = {'0': 0, '1': 0}
        for bit in bit_string:
            if bit in counts:
                counts[bit] += 1
        
        total = len(bit_string)
        if total == 0:
            return 0.0
            
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return entropy
    
    def benchmark_methods(self, runs: int = 100) -> Dict:
        """Benchmark all methods for speed and quality"""
        methods = ['hadamard', 'bell', 'ghz', 'nist']
        results = {}
        
        for method in methods:
            times = []
            entropies = []
            
            for i in range(runs):
                start_time = time.time()
                
                if method == 'hadamard':
                    result = self.hadamard_method(shots=100)
                elif method == 'bell':
                    result = self.bell_state_method(shots=100)
                elif method == 'ghz':
                    result = self.ghz_state_method(shots=100)
                else:
                    result = self.nist_compliant_method(shots=100)
                
                end_time = time.time()
                
                if 'error' not in result:
                    times.append(end_time - start_time)
                    entropies.append(result['entropy'])
            
            if times:  # Only add if we have successful runs
                results[method] = {
                    'avg_time': np.mean(times),
                    'std_time': np.std(times),
                    'avg_entropy': np.mean(entropies),
                    'std_entropy': np.std(entropies),
                    'min_time': np.min(times),
                    'max_time': np.max(times),
                    'successful_runs': len(times)
                }
        
        return results
