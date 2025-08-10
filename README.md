# Quantum Advantage in Probability Estimation

This project demonstrates the quadratic speedup of Quantum Amplitude Estimation (QAE) over Classical Monte Carlo (CMC) methods for estimating a probability, a core task in many scientific domains like high-energy physics.

The simulation compares the convergence rate of both methods, showing that QAE achieves a desired precision with significantly fewer oracle calls. The project is structured as a modular Python application to showcase best practices in software development for scientific computing.

## Key Concepts
- **Classical Monte Carlo (CMC):** A statistical method that relies on random sampling. Its estimation error converges at a rate of **O(1/√M)**, where M is the number of samples.
- **Quantum Amplitude Estimation (QAE):** A quantum algorithm that can estimate a probability encoded in a quantum state's amplitude. Its error converges at a rate of **O(1/M)**, providing a quadratic speedup over CMC.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/quantum-monte-carlo-project.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd quantum-monte-carlo-project
    ```
3.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use `venv\Scripts\activate`
    ```
4.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the full simulation and generate the comparison plot, execute the main script from the root directory:
```bash
python src/main.py
