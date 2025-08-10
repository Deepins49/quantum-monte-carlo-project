# src/quantum_simulation.py

import math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# --- QAE Operators ---
def get_qae_operators(p_true):
    """Builds the A and Q operators for QAE."""
    theta_p = 2 * math.asin(math.sqrt(p_true))
    
    # A: State preparation operator
    A = QuantumCircuit(1, name="A")
    A.ry(theta_p, 0)

    # Q: Grover-like oracle
    Q = QuantumCircuit(1, name="Q")
    Q.compose(A, inplace=True)
    Q.z(0)
    Q.compose(A.inverse(), inplace=True)
    Q.z(0)
    
    return A, Q.to_gate()

# --- Analysis Functions ---
def full_counts_probs(counts: dict, num_bits: int):
    """Converts a counts dictionary to a full probability vector."""
    shots_total = sum(counts.values())
    if shots_total == 0:
        return {j: 0.0 for j in range(2**num_bits)}
        
    probs = {j: 0.0 for j in range(2**num_bits)}
    for bitstr, cnt in counts.items():
        j = int(bitstr, 2)
        probs[j] = cnt / shots_total
    return probs

def weighted_estimator_from_probs(probs: dict, m: int):
    """Calculates the probability estimate using a weighted average."""
    s = 0.0
    for j, pj in probs.items():
        phase = j / (2**m)
        s += pj * (math.sin(math.pi * phase))**2
    return s

def bootstrap_ci(counts: dict, m: int, shots: int, n_boot: int):
    """Calculates a 95% confidence interval for the weighted estimator."""
    probs = full_counts_probs(counts, m)
    pvec = np.array([probs.get(j, 0.0) for j in range(2**m)])
    
    estimates = []
    for _ in range(n_boot):
        resampled_counts = np.random.multinomial(shots, pvec)
        resampled_probs = {j: count / shots for j, count in enumerate(resampled_counts)}
        est = weighted_estimator_from_probs(resampled_probs, m)
        estimates.append(est)
        
    arr = np.array(estimates)
    lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
    return lo, hi

# --- Main Simulation Runner ---
def run_qae_simulation(p_true, m_values, shots, seed, use_noise=False):
    """
    Runs the full QAE simulation for a range of m values.
    Returns results for both an ideal and a noisy simulator.
    """
    print("--- Starting Quantum Amplitude Estimation Simulation ---")
    
    # Prepare simulators
    sim_ideal = AerSimulator()
    sim_noisy = None
    if use_noise:
        noise = NoiseModel()
        noise.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ['u1', 'u2', 'u3', 'ry', 'rz'])
        noise.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ['cx'])
        sim_noisy = AerSimulator(noise_model=noise, seed_simulator=seed)
        print("Using a custom depolarizing noise model.")

    A_op, Q_gate = get_qae_operators(p_true)
    c_Q_gate = Q_gate.control(1)

    results = {
        'ideal': {'p_est': [], 'ci_lo': [], 'ci_hi': []},
        'noisy': {'p_est': [], 'ci_lo': [], 'ci_hi': []}
    }

    for m in m_values:
        print(f"Running for m = {m} ({2**m} Oracle Calls)")
        qpe = QuantumCircuit(m + 1, m, name=f"QPE_m{m}")
        qpe.compose(A_op, qubits=[m], inplace=True)
        qpe.h(range(m))
        for i in range(m):
            for _ in range(2**i):
                qpe.append(c_Q_gate, [i, m])
        qpe.append(QFT(m, inverse=True).to_gate(), range(m))
        qpe.measure(range(m), range(m))

        # Run on ideal simulator
        tqc_ideal = transpile(qpe, sim_ideal, seed_transpiler=seed)
        counts_ideal = sim_ideal.run(tqc_ideal, shots=shots, seed_simulator=seed).result().get_counts()
        probs_ideal = full_counts_probs(counts_ideal, m)
        p_est_ideal = weighted_estimator_from_probs(probs_ideal, m)
        lo_i, hi_i = bootstrap_ci(counts_ideal, m, shots, n_boot=200)
        results['ideal']['p_est'].append(p_est_ideal)
        results['ideal']['ci_lo'].append(lo_i)
        results['ideal']['ci_hi'].append(hi_i)

        # Run on noisy simulator
        if use_noise and sim_noisy:
            tqc_noisy = transpile(qpe, sim_noisy, seed_transpiler=seed)
            counts_noisy = sim_noisy.run(tqc_noisy, shots=shots, seed_simulator=seed).result().get_counts()
            probs_noisy = full_counts_probs(counts_noisy, m)
            p_est_noisy = weighted_estimator_from_probs(probs_noisy, m)
            lo_n, hi_n = bootstrap_ci(counts_noisy, m, shots, n_boot=200)
            results['noisy']['p_est'].append(p_est_noisy)
            results['noisy']['ci_lo'].append(lo_n)
            results['noisy']['ci_hi'].append(hi_n)
    
    print("--- Quantum Simulation Complete ---")
    return results
