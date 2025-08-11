# src/quantum_galton_board.py

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from scipy.stats import binom

def create_qgb_circuit(layers: int, thetas: list = None):
    """
    Creates a quantum circuit to simulate an L-layer Galton Board.

    Args:
        layers (int): The number of layers for the Galton Board.
        thetas (list, optional): A list of theta values for Ry gates for each
            layer to create a biased distribution. If None, uses Hadamard
            gates for a standard 50/50 binomial distribution. Defaults to None.

    Returns:
        QuantumCircuit: The Qiskit circuit for the simulation.
    """
    qc = QuantumCircuit(layers, layers, name=f"QGB_{layers}L")
    
    if thetas is None:
        # Standard QGB: Creates a Binomial(L, 0.5) distribution (Hadamard Walk)
        # This approximates a Gaussian for large L.
        qc.h(range(layers))
    else:
        if len(thetas) != layers:
            raise ValueError("Length of thetas must match the number of layers.")
        # Biased QGB: Each layer has a specific left/right probability
        for i in range(layers):
            # The probability of measuring '1' is sin^2(theta/2)
            qc.ry(thetas[i], i)
            
    qc.measure(range(layers), range(layers))
    return qc

def get_thetas_for_exponential(layers: int, scale: float):
    """
    Calculates Ry rotation angles to approximate an exponential distribution.
    
    The final distribution of k '1's in the output will be a Binomial B(n,p).
    To make this approximate an exponential distribution, we can match their means.
    Mean of Binomial = n*p. Mean of Exponential = scale.
    So, n*p = scale  =>  p = scale/n.
    
    Args:
        layers (int): The number of layers (n).
        scale (float): The scale parameter (lambda) of the target exponential distribution.

    Returns:
        list: A list of theta values for the Ry gates.
    """
    prob_one = scale / layers
    if not (0 <= prob_one <= 1.0):
        raise ValueError(f"Scale ({scale}) is not valid for {layers} layers. Results in p={prob_one:.3f}, which is outside [0,1].")
        
    # p = sin^2(theta/2) => theta = 2 * asin(sqrt(p))
    theta = 2 * np.arcsin(np.sqrt(prob_one))
    
    # Use the same theta for all layers for a simple, independent-step approximation
    return [theta] * layers

def get_thetas_for_hadamard_walk(layers: int):
    """
    A Hadamard walk is the standard, unbiased Galton Board.
    This is equivalent to using H gates, which is the default behavior
    when `thetas` is None.
    """
    return None
