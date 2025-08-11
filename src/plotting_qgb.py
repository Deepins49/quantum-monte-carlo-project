# src/plotting_qgb.py

import matplotlib.pyplot as plt
import os

def plot_qgb_distribution(experimental, theoretical, dist_type, layers, use_noise, save_path=None):
    """
    Plots the experimental and theoretical QGB distributions and saves the figure.

    Args:
        experimental (dict): Dictionary of experimental probabilities.
        theoretical (dict): Dictionary of theoretical probabilities.
        dist_type (str): The name of the distribution (e.g., 'normal', 'exponential').
        layers (int): The number of layers simulated.
        use_noise (bool): Flag indicating if noise was used, for plot title.
        save_path (str, optional): Path to save the plot image. Defaults to None.
    """
    print(f"--- Generating Plot for {dist_type.capitalize()} Distribution ---")
    
    bin_labels = list(theoretical.keys())
    exp_values = [experimental.get(k, 0) for k in bin_labels] # Ensure all bins are present
    the_values = list(theoretical.values())

    plt.figure(figsize=(12, 7))
    
    # Plot experimental results as a bar chart
    plt.bar(bin_labels, exp_values, color='skyblue', label='Experimental (Quantum)', zorder=2)
    # Plot theoretical results as a line/marker plot
    plt.plot(bin_labels, the_values, 'o-', color='red', label='Theoretical Target', zorder=3)
    
    noise_str = "Noisy" if use_noise else "Ideal"
    title = f"{noise_str} QGB for {dist_type.capitalize()} Distribution ({layers} Layers)"
    
    plt.xlabel("Final Bin (Number of '1's)", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.title(title, fontsize=14)
    plt.xticks(bin_labels)
    plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=1)
    plt.legend()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")

    # Use plt.close() to prevent plots from displaying in the console when running the script
    plt.close()
