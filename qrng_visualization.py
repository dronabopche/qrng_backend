import matplotlib.pyplot as plt
import numpy as np
from qiskit.visualization import plot_histogram
from typing import Dict, List

class QRNGVisualizer:
    def __init__(self):
        self.fig_size = (12, 8)
        plt.style.use('default')  # Use default style for compatibility
    
    def plot_distribution_comparison(self, quantum_counts: Dict, classical_bits: List[str], title: str = "Distribution Comparison"):
        """Compare quantum vs classical distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.fig_size)
        
        # Quantum distribution
        if quantum_counts:
            plot_histogram(quantum_counts, ax=ax1)
        ax1.set_title(f'Quantum Distribution - {title}')
        
        # Classical distribution (pseudo-random)
        classical_counts = {}
        for bit in classical_bits:
            classical_counts[bit] = classical_counts.get(bit, 0) + 1
        
        if classical_counts:
            plot_histogram(classical_counts, ax=ax2)
        ax2.set_title(f'Classical Distribution - {title}')
        
        plt.tight_layout()
        return fig
    
    def plot_entropy_trend(self, entropy_data: Dict):
        """Plot entropy trends across methods"""
        methods = list(entropy_data.keys())
        entropies = [entropy_data[method] for method in methods]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        bars = ax.bar(methods, entropies, color=colors[:len(methods)])
        
        ax.set_ylabel('Entropy (bits)')
        ax.set_xlabel('Methods')
        ax.set_title('Entropy Comparison of QRNG Methods')
        ax.set_ylim(0, max(entropies) * 1.1 if entropies else 1)
        
        # Add value labels on bars
        for bar, entropy in zip(bars, entropies):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{entropy:.3f}', ha='center', va='bottom')
        
        return fig
    
    def plot_benchmark_results(self, benchmark_results: Dict):
        """Plot benchmarking results"""
        methods = list(benchmark_results.keys())
        times = [benchmark_results[method]['avg_time'] for method in methods]
        entropies = [benchmark_results[method]['avg_entropy'] for method in methods]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.fig_size)
        
        # Time comparison
        bars1 = ax1.bar(methods, times, color='lightcoral')
        ax1.set_ylabel('Average Time (seconds)')
        ax1.set_title('Execution Time Comparison')
        ax1.set_ylim(0, max(times) * 1.2 if times else 1)
        
        # Entropy comparison
        bars2 = ax2.bar(methods, entropies, color='lightseagreen')
        ax2.set_ylabel('Average Entropy (bits)')
        ax2.set_title('Randomness Quality Comparison')
        ax2.set_ylim(0, max(entropies) * 1.2 if entropies else 1)
        
        # Add value labels
        for bars, ax, values in zip([bars1, bars2], [ax1, ax2], [times, entropies]):
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.001,
                       f'{value:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
