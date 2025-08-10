# src/plotting.py

import matplotlib.pyplot as plt
import numpy as np
import os

def generate_convergence_plot(classical_errors, quantum_results, p_true, M_values, save_path=None):
    """
    Generates and saves a log-log plot comparing classical and quantum convergence.
    """
    print("--- Generating Convergence Plot ---")
    plt.figure(figsize=(12, 7))

    # Plot Classical MC
    plt.plot(M_values, classical_errors, 'o-', color='gray', label='Classical MC (Error ~1/√M)')

    # Plot Ideal Quantum
    ideal_p_ests = quantum_results['ideal']['p_est']
    ideal_ci_lo = quantum_results['ideal']['ci_lo']
    ideal_ci_hi = quantum_results['ideal']['ci_hi']
    y_err_ideal = [np.array(ideal_p_ests) - np.array(ideal_ci_lo), np.array(ideal_ci_hi) - np.array(ideal_p_ests)]
    plt.errorbar(M_values, [abs(v - p_true) for v in ideal_p_ests], yerr=y_err_ideal,
                 fmt='s-', capsize=5, color='blue', label='Ideal QAE (Error ~1/M)')

    # Plot Noisy Quantum if available
    if quantum_results['noisy']['p_est']:
        noisy_p_ests = quantum_results['noisy']['p_est']
        noisy_ci_lo = quantum_results['noisy']['ci_lo']
        noisy_ci_hi = quantum_results['noisy']['ci_hi']
        y_err_noisy = [np.array(noisy_p_ests) - np.array(noisy_ci_lo), np.array(noisy_ci_hi) - np.array(noisy_p_ests)]
        plt.errorbar(M_values, [abs(v - p_true) for v in noisy_p_ests], yerr=y_err_noisy,
                     fmt='x-', capsize=5, color='red', label='Noisy QAE')

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Number of Oracle Queries (M)', fontsize=12)
    plt.ylabel('Estimation Error |p_est - p_true|', fontsize=12)
    plt.title(f'QAE vs Classical MC Estimation (p_true = {p_true})', fontsize=14)
    plt.grid(True, which='both', ls='--')
    plt.legend()

    if save_path:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
    
    plt.show()
