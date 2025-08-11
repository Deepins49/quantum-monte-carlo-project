# src/main_qgb.py

# --- Main execution script for the Quantum Galton Board simulation challenge ---

# NEW - Explicitly relative
from .quantum_galton_board import create_qgb_circuit, get_thetas_for_exponential, get_thetas_for_hadamard_walk
from .analysis import run_simulation, process_results, get_target_distribution, bootstrap_distance
from .plotting_qgb import plot_qgb_distribution

def run_and_analyze_single_case(dist_type: str, layers: int, shots: int, seed: int, use_noise: bool):
    """
    Orchestrates a full simulation run for a single case (e.g., normal/ideal).
    This function handles creating, running, analyzing, and plotting for one scenario.
    """
    print(f"\n{'='*25} RUNNING CASE: {dist_type.upper()} ({'Noisy' if use_noise else 'Ideal'}) {'='*25}")
    
    # 1. Get parameters (thetas) for the circuit based on the desired distribution
    if dist_type == 'normal':
        thetas = get_thetas_for_hadamard_walk(layers) # This will be None to use H-gates
    elif dist_type == 'exponential':
        # We set the scale of the exponential relative to the number of layers
        # A scale of layers/4 creates a reasonably distinct exponential shape
        thetas = get_thetas_for_exponential(layers, scale=layers/4.0)
    else:
        raise TypeError(f"Unsupported distribution type: {dist_type}")

    # 2. Create the quantum circuit
    circuit = create_qgb_circuit(layers, thetas)
    
    # 3. Run the simulation (either ideal or with noise)
    # The run_simulation function handles transpilation and execution
    counts = run_simulation(circuit, shots, seed, use_noise=use_noise)
    
    # 4. Process the raw counts and get the target theoretical distribution
    experimental_dist = process_results(counts, layers)
    target_dist = get_target_distribution(dist_type, layers, scale=layers/4.0)
    
    # 5. Analyze the distance between the distributions, including stochastic uncertainty
    mean_dist, ci_lo, ci_hi = bootstrap_distance(counts, layers, target_dist)
    print(f"Distance (KL Divergence): {mean_dist:.4f} (95% CI: [{ci_lo:.4f}, {ci_hi:.4f}])")
    
    # 6. Plot the results
    noise_str = "Noisy" if use_noise else "Ideal"
    plot_save_path = f"results/{dist_type}_{noise_str}_{layers}L.png"
    plot_qgb_distribution(experimental_dist, target_dist, dist_type, layers, use_noise, save_path=plot_save_path)

def main():
    """Main function to run all the required scenarios for the challenge."""
    
    # --- Simulation Parameters ---
    LAYERS = 14      # Maximize layers while keeping simulation time reasonable
    SHOTS = 8192     # Standard number of shots
    SEED = 42        # For reproducibility

    # --- Fulfill Deliverable #2 & #3 (using an Ideal Simulator) ---
    # Normal (Gaussian-like) distribution from a Hadamard walk
    run_and_analyze_single_case('normal', LAYERS, SHOTS, SEED, use_noise=False)
    # Exponential distribution
    run_and_analyze_single_case('exponential', LAYERS, SHOTS, SEED, use_noise=False)

    # --- Fulfill Deliverable #4 & #5 (using a Noisy Simulator) ---
    # Normal (Gaussian-like) distribution on a noisy backend
    run_and_analyze_single_case('normal', LAYERS, SHOTS, SEED, use_noise=True)
    # Exponential distribution on a noisy backend
    run_and_analyze_single_case('exponential', LAYERS, SHOTS, SEED, use_noise=True)
    
    print(f"\n{'='*25} ALL SIMULATIONS COMPLETE {'='*25}")

if __name__ == "__main__":
    main()
