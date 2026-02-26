# QSD Computational Suite

Python implementations for computing, validating, and visualizing all Quantum Spectrodynamics predictions.

## Module Overview

### Core (NumPy + SciPy only)

| Module | Description | Run |
|---|---|---|
| `qsd_constants.py` | **Single source of truth.** Defines the QSD triad (Hb₄, ς, ϖ) and derives all physical predictions. Prints a full comparison table when run as a script. | `python qsd_constants.py` |
| `qsd_simulation_suite.py` | Numerical simulations: eigenvalue analysis of [[5,1,3]] stabilizers, K₄ Heisenberg model ground states, energy scale cascades, and syndrome extraction. | `python qsd_simulation_suite.py` |
| `qsd_monte_carlo.py` | Monte Carlo validation of QSD error bounds across all predicted observables. Statistical analysis with confidence intervals. | `python qsd_monte_carlo.py` |

### Visualization (+ Matplotlib)

| Module | Description | Output |
|---|---|---|
| `qsd_visualizations.py` | Publication-quality static figures: coupling derivation diagrams, energy scale hierarchies, prediction comparison plots. | `figures/*.png` |
| `qsd_animations.py` | Animated GIFs: K₄+C₅ dynamics, [[5,1,3]] error correction cycles, renormalization flow, energy cascade. | `figures/*.gif` |
| `qsd_syndrome_production.py` | Syndrome energy production cross-sections and dimuon excess analysis. | `figures/*.png` |

### Quantum Circuits (+ Qiskit)

| Module | Description | Requires |
|---|---|---|
| `qsd_qiskit_suite.py` | Nine quantum circuit simulations: [[5,1,3]] code verification, K₄ Heisenberg VQE, C₅ eigenvalue circuits, stabilizer measurements, and more. | Qiskit ≥ 1.0, Qiskit-Aer ≥ 0.13 |
| `qsd_qiskit_additions.py` | Extended experiments: Trotter evolution, Mathieu equation circuits, advanced VQE variants. Imports from `qsd_qiskit_suite.py`. | Qiskit ≥ 1.0, Qiskit-Aer ≥ 0.13 |

## Dependency Graph

```
qsd_constants.py                  ← All modules import from here
    ├── qsd_simulation_suite.py
    ├── qsd_monte_carlo.py
    ├── qsd_animations.py
    ├── qsd_visualizations.py
    ├── qsd_syndrome_production.py
    └── qsd_qiskit_suite.py
         └── qsd_qiskit_additions.py
```

## Quick Start

```bash
# Activate the conda environment (from repository root)
conda activate qsd

# Print all QSD predictions and experimental comparisons
python qsd_constants.py

# Run the full numerical simulation suite
python qsd_simulation_suite.py

# Generate all publication figures (creates figures/ directory)
python qsd_visualizations.py
python qsd_animations.py

# Monte Carlo validation (may take a few minutes)
python qsd_monte_carlo.py

# Quantum circuit simulations (requires Qiskit)
python qsd_qiskit_suite.py
python qsd_qiskit_additions.py
```

## Output

Visualization scripts create a `figures/` subdirectory containing:

- Static PNG plots suitable for publication
- Animated GIF visualizations of QSD mechanisms
- All figures are generated at 300 DPI with LaTeX-compatible fonts

## Notes

- All modules use `matplotlib.rcParams["text.usetex"] = False` for portability. Set to `True` if you have LaTeX installed and want rendered math in figures.
- The Qiskit modules use conditional imports — they fall back gracefully and provide matrix-only computation if Qiskit is not installed.
- All computations carry 15+ significant figures internally; only display values are rounded.
