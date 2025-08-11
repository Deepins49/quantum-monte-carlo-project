# src/main.py

# --- Main execution script for the Quantum vs Classical simulation ---

# Import the necessary functions from our modules
# NEW
from classical_simulation import run_classical_mc
from quantum_simulation import run_qae_simulation
from plotting import generate_convergence_plot

def main():
    """Main function to orchestrate the simulation and plotting."""
    
    # --- Simulation Parameters ---
    P_TRUE = 0.12         # The "true" probability we are trying to estimate
    SHOTS = 4096          # Number of shots for each quantum circuit run
    SEED = 42             # Seed for reproducibility
    USE_NOISE = True      # Set to True to include the noisy simulation
    
    # M_values define the number of "queries" or "samples"
    # For quantum, m_values are the number of evaluation qubits
    m_values = list(range(3, 8))
    M_values = [2**m for m in m_values]

    # --- Run Simulations ---
    classical_errors = run_classical_mc(P_TRUE, M_values, SEED)
    quantum_results = run_qae_simulation(P_TRUE, m_values, SHOTS, SEED, use_noise=USE_NOISE)

    # --- Generate Final Plot ---
    plot_save_path = "results/convergence_plot.png"
    generate_convergence_plot(classical_errors, quantum_results, P_TRUE, M_values, save_path=plot_save_path)

if __name__ == "__main__":
    main()
