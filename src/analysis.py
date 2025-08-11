# src/analysis.py

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from scipy.stats import binom

# Note: I've removed `expon` from scipy.stats as we generate the target
# distribution for the exponential case using the binomial theorem directly,
# which is more accurate to what the circuit actually produces.

def process_results(counts: dict, layers: int):
    """Processes circuit results into a probability distribution based on Hamming weight."""
    num_shots = sum(counts.values())
    if num_shots == 0:
        return {k: 0 for k in range(layers + 1)}
        
    final_bins = {k: 0 for k in range(layers + 1)}
    for bitstring, count in counts.items():
        num_ones = bitstring.count('1')
        final_bins[num_ones] += count
        
    return {k: v / num_shots for k, v in final_bins.items()}

def get_target_distribution(dist_type: str, layers: int, scale: float = 3.0):
    """Gets the ideal theoretical probability distribution."""
    bins = range(layers + 1)
    if dist_type == 'normal': # This is the Binomial(n, 0.5) from the Hadamard walk
        probs = binom.pmf(bins, layers, p=0.5)
    elif dist_type == 'exponential':
        # The circuit produces a Binomial(n, p) distribution. We choose p
        # to make this distribution resemble an exponential.
        prob_one = scale / layers
        if not (0 <= prob_one <= 1.0):
             raise ValueError(f"Scale ({scale}) is not valid for {layers} layers.")
        probs = binom.pmf(bins, layers, p=prob_one)
    else:
        raise ValueError(f"Unknown distribution type: {dist_type}")
        
    return {k: prob for k, prob in zip(bins, probs)}

def kl_divergence(p, q):
    """Calculates the Kullback-Leibler divergence D_KL(P || Q)."""
    p_keys = p.keys()
    q_keys = q.keys()
    all_keys = sorted(list(set(p_keys) | set(q_keys)))
    
    p_vals = np.array([p.get(k, 0) for k in all_keys])
    q_vals = np.array([q.get(k, 0) for k in all_keys])
    
    # Add a small epsilon to avoid log(0) issues
    epsilon = 1e-12
    p_vals += epsilon
    q_vals += epsilon
    
    return np.sum(p_vals * np.log(p_vals / q_vals))

def bootstrap_distance(counts: dict, layers: int, target_dist: dict, n_boot: int = 500):
    """
    Uses bootstrapping to find a confidence interval for the KL divergence.
    This accounts for stochastic uncertainty from finite shots.
    """
    num_shots = sum(counts.values())
    
    # Create a probability vector of the raw bitstring outcomes
    raw_p_vec = [counts.get(format(i, f'0{layers}b'), 0) / num_shots for i in range(2**layers)]
    
    distances = []
    for _ in range(n_boot):
        # Resample from the multinomial distribution of raw outcomes
        resampled_raw_counts_arr = np.random.multinomial(num_shots, raw_p_vec)
        resampled_raw_counts_dict = {format(i, f'0{layers}b'): count for i, count in enumerate(resampled_raw_counts_arr)}
        
        # Process the resampled outcomes into the final binned distribution
        resampled_dist = process_results(resampled_raw_counts_dict, layers)
        
        # Calculate distance for this bootstrap sample
        dist = kl_divergence(resampled_dist, target_dist)
        distances.append(dist)
        
    mean_dist = np.mean(distances)
    ci_lo = np.percentile(distances, 2.5)
    ci_hi = np.percentile(distances, 97.5)
    return mean_dist, ci_lo, ci_hi

def run_simulation(circuit, shots, seed, use_noise=False):
    """Runs a circuit on an ideal or noisy simulator."""
    if use_noise:
        # A simple, optimizable noise model. You can make this more complex.
        noise_model = NoiseModel()
        # Add some error to single-qubit gates
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ["ry", "h"])
        # Add a larger error to two-qubit gates (though our simple QGB doesn't use them)
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ["cx"])
        simulator = AerSimulator(noise_model=noise_model)
        # For optimization, you could try different transpiler levels.
        # Level 3 is aggressive and good for reducing gate count on noisy backends.
        t_circuit = transpile(circuit, simulator, seed_transpiler=seed, optimization_level=3)
    else:
        simulator = AerSimulator()
        t_circuit = transpile(circuit, simulator, seed_transpiler=seed)
        
    print(f"Running circuit with depth: {t_circuit.depth()}, ops: {t_circuit.count_ops()}")
    result = simulator.run(t_circuit, shots=shots, seed_simulator=seed).result()
    return result.get_counts()
