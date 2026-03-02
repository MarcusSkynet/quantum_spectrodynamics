# Quantum Spectrodynamics (QSD)

**Deriving Standard Model Parameters from the Geometry of Quantum Error-Correcting Codes**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18832273.svg)](https://doi.org/10.5281/zenodo.18832273)

---

## Overview

Quantum Spectrodynamics (QSD) is a theoretical framework that derives fundamental
physics constants — gauge couplings, particle masses, and the cosmological constant —
from the algebraic geometry of the **$[[5,1,3]]$ quantum error-correcting code**.

The framework requires **zero free parameters** beyond the Planck mass (CODATA 2018). All predictions
emerge from three constants (the *QSD triad*) that arise naturally from the code's
topology:

| Constant | Symbol | Expression | Value |
|---|---|---|---|
| Holographic bit density | $Hb_4$ | $1/(4 \ln 2)$ | 0.36067 |
| Geometric strain | $\varsigma$ | $3/(80 \varphi^2)$ | 0.01432 |
| Spectral bond | $\varpi$ | $\pi\varphi^2$ | 8.22480 |

where $\varphi=(1+\sqrt{5})/2$ is the golden ratio.

### Key Predictions vs. Experiment

| Symbol | Observable | QSD Prediction | Experimental Value | Source | Agreement |
|---|---|---|---|---|---|
| $\alpha^{-1}$ | Fine structure constant | 137.0330 | 137.0360 | CODATA 2018 | 22 ppm |
| $\alpha_s$ | Strong coupling at $M_Z$ | 0.11781 | 0.1180 | PDG 2022 | 0.16% |
| $\sin^2\theta_W$ | Weak mixing angle | 0.23122 | 0.23122 | PDG 2022 | 0.004% |
| $m_H$ | Higgs boson mass | 126.7 GeV | 125.25 GeV | PDG 2022 | 1.2% |
| $m_W$ | W boson mass | 81.1 GeV | 80.377 GeV | PDG 2022 | 0.9% |
| $\log(\rho_\Lambda/\rho_{Pl})$ | Cosmological constant | −121.28 | −121.27 | Planck 2018 | 0.008% |

The **syndrome energy $E_{syn} \approx 28.2$ GeV** is a novel QSD prediction corresponding to
the dimuon excess observed by CMS at $\sqrt{s} \approx 28.3$ GeV.

---

## Repository Structure

```
quantum-spectrodynamics/
├── LICENSE                               CC BY 4.0
├── README.md                             This file
├── CITATION.cff                          Machine-readable citation metadata
├── RELEASE_NOTES.md                      Zenodo release notes for v1.0
├── environment.yml                       Conda environment for running all code
├── Makefile                              Build PDFs from LaTeX sources
├── .gitignore
│
├── tex/                                  LaTeX source files
│   ├── README.md
│   ├── qsd_main_preprint.tex             Main paper
│   ├── qsd_s1_formal_proofs.tex          S1: Formal proofs
│   ├── qsd_s2_energy_scale.tex           S2: Energy scale and dressing
│   ├── qsd_s3_lagrangian.tex             S3: QSD Lagrangian derivation
│   ├── qsd_s4_renormalization.tex        S4: Topological renormalization
│   ├── qsd_s5_syndrome_prediction.tex    S5: Syndrome prediction & proton stability
│   ├── qsd_s6_string_correspondence.tex  S6: String theory correspondence
│   ├── qsd_s7_cosmological_constant.tex  S7: Cosmological constant (speculative extension)
│   ├── qsd_tn1_hb_redefinition.tex       TN-1: Hb redefinition note
│   ├── qsd_references.bib                Shared bibliography (175+ references)
│   └── qsd_preamble.tex                  Unified notation definitions
│
├── pdf/                                  Pre-compiled PDFs (for immediate reading)
│   └── README.md
│
├── code/                                 Python simulation & computation suite
│   ├── README.md
│   ├── __init__.py
│   ├── qsd_constants.py                  Single source of truth for all QSD constants
│   ├── qsd_simulation_suite.py           Numerical simulations (no Qiskit needed)
│   ├── qsd_monte_carlo.py                Monte Carlo validation of error bounds
│   ├── qsd_animations.py                 Animated GIF visualizations
│   ├── qsd_visualizations.py             Static publication-quality figures
│   ├── qsd_syndrome_production.py        Syndrome energy production analysis
│   ├── qsd_qiskit_suite.py               Quantum circuit simulations (Qiskit)
│   └── qsd_qiskit_additions.py           Extended quantum experiments
│
└── visualizations/                       Interactive 3D visualizations (Three.js)
    ├── README.md
    ├── qsd_4simplex.html                 4-Simplex geometry explorer
    ├── qsd_4simplex_network.html         Tensor network of 4 code blocks
    └── qsd_4simplex_snap_mechanism.html  Snap mechanism animation
```

---

## Quick Start

### Read the Papers

Pre-compiled PDFs are in [`pdf/`](pdf/). Start with the main preprint, then
consult supplements S1–S7 for detailed derivations.

### Run the Code

```bash
# Clone the repository
git clone https://github.com/[username]/quantum-spectrodynamics.git
cd quantum-spectrodynamics

# Create the conda environment
conda env create -f environment.yml
conda activate qsd

# Run the master constants module (prints all predictions)
cd code
python qsd_constants.py

# Generate publication figures
python qsd_visualizations.py

# Run Monte Carlo validation
python qsd_monte_carlo.py

# Run quantum circuit simulations (requires Qiskit)
python qsd_qiskit_suite.py
```

### View Interactive Visualizations

Open any `.html` file in `visualizations/` directly in a web browser —
no server required. These are self-contained Three.js applications.

### Compile LaTeX Sources

```bash
# Build all PDFs (requires TeX Live or similar distribution)
make all

# Build a single document
cd tex
pdflatex qsd_main_preprint.tex
bibtex qsd_main_preprint
pdflatex qsd_main_preprint.tex
pdflatex qsd_main_preprint.tex
```

---

## Theoretical Foundation

QSD begins from a single structural postulate: the physical vacuum encodes
information through the $[[5,1,3]]$ quantum error-correcting code. The five
physical qubits form a complete graph $K_4$ embedded in a 5-cycle $C_5$, creating a
geometric frustration whose resolution yields the gauge couplings of the
Standard Model.

### The Derivation Chain

1. **Code geometry → Triad constants** $(Hb_4,\,\varsigma,\,\varpi($ emerge from the
   $[[5,1,3]]$ code's topological invariants.
2. **Triad → Gauge couplings** via 3-loop topological renormalization on the
   $K_4–C_5$ graph structure.
3. **Triad → Energy scale** through the $2^{60}$ information compression factor
   from Planck to electroweak scale.
4. **Triad → Mass spectrum** from syndrome extraction eigenvalues of the code.
5. **Triad → Cosmological constant** via the entropy barrier
   $4/\varsigma \approx 279.3$ nats (speculative).

Each step is derived algebraically with no fitted parameters. All derivations
are documented across the main preprint and supplements S1–S7.

---

## Code Architecture

All Python modules share a single source of truth:

```
qsd_constants.py                   ← Every other module imports from here
    ├── qsd_simulation_suite.py      (NumPy/SciPy only)
    ├── qsd_monte_carlo.py           (NumPy/SciPy + statistics)
    ├── qsd_animations.py            (+ matplotlib animations)
    ├── qsd_visualizations.py        (+ matplotlib static plots)
    ├── qsd_syndrome_production.py   (+ matplotlib + scipy.integrate)
    └── qsd_qiskit_suite.py          (+ Qiskit)
         └── qsd_qiskit_additions.py (+ extended experiments)
```

The core modules (`qsd_constants.py`, `qsd_simulation_suite.py`,
`qsd_monte_carlo.py`) require only NumPy and SciPy. Qiskit is needed only
for the quantum circuit simulations in `qsd_qiskit_suite.py` and
`qsd_qiskit_additions.py`.

---

## Dependencies

See [`environment.yml`](environment.yml) for the full conda specification.

**Core** (required for all modules):
- Python ≥ 3.10
- NumPy ≥ 1.24
- SciPy ≥ 1.10

**Visualization** (for figures and animations):
- Matplotlib ≥ 3.7

**Quantum circuits** (optional — for Qiskit simulations):
- Qiskit ≥ 1.0
- Qiskit-Aer ≥ 0.13

**LaTeX compilation** (optional — pre-compiled PDFs included):
- TeX Live 2023+ or equivalent
- Packages: amsmath, physics, tikz, hyperref, booktabs

---

## Citation

If you use this work, please cite:

```bibtex
@misc{hubka2026qsd,
  author  = {Hubka, Marek},
  title   = {Quantum Spectrodynamics: Deriving Standard Model Parameters
             from the Geometry of Quantum Error-Correcting Codes},
  year    = {2026},
  doi     = {10.5281/zenodo.18832273},
  note    = {Independent research preprint with seven supplements}
}
```

See [`CITATION.cff`](CITATION.cff) for machine-readable metadata.

---

## License

This work is licensed under [Creative Commons Attribution 4.0 International
(CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this material for any purpose, provided you
give appropriate credit.

---

## Author

**Marek Hubka**
Independent Researcher, Czech Republic

---

*Quantum Spectrodynamics v1.0.0 — March 2026*
