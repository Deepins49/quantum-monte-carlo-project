
# src/classical_simulation.py

import numpy as np

def run_classical_mc(p_true, M_values, seed):
    """
    Runs a classical Monte Carlo simulation to estimate a probability.

    Returns:
        list: A list of absolute errors for each value in M_values.
    """
    print("--- Starting Classical Monte Carlo Simulation ---")
    np.random.seed(seed)
    errors = []
    for M in M_values:
        # Simulate M random "events"
        success_count = (np.random.rand(M) < p_true).sum()
        p_est = success_count / M
        errors.append(abs(p_est - p_true))
    print("--- Classical Simulation Complete ---")
    return errors
