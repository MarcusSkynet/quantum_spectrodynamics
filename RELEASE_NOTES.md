# Release Notes — Quantum Spectrodynamics v1.0.0

**Release date:** February 2026

**DOI:** 10.5281/zenodo.XXXXXXX

**License:** CC BY 4.0

---

## Summary

This is the first public release of **Quantum Spectrodynamics (QSD)**, a theoretical
framework that derives fundamental physics constants from the algebraic geometry of
the $[[5,1,3]]$ quantum error-correcting code. The release comprises the complete
manuscript suite, computational tools, and interactive visualizations.

---

## What Is QSD?

Quantum Spectrodynamics posits that the physical vacuum encodes information through
the $[[5,1,3]]$ quantum error-correcting code — the smallest code capable of correcting
an arbitrary single-qubit error. From this single structural postulate, the framework
derives the gauge couplings, particle masses, and cosmological constant of the
Standard Model with **zero free parameters** beyond the Planck mass.

The core insight is that the $[[5,1,3]]$ code's five physical qubits form a complete
graph $K_4$ embedded in a 5-cycle $C_5$, creating a geometric frustration whose algebraic
resolution yields three fundamental constants (the *QSD triad*):

- **Holographic bit density** $Hb_4 = 1/(4 \ln 2) \approx 0.3607$
- **Geometric strain** $\varsigma = 3/(80 \varphi^2) \approx 0.01432$
- **Spectral bond** $\varpi = \pi\varphi^2 \approx 8.2248$

Every Standard Model parameter then follows from algebraic combinations of these
three quantities plus the Planck mass.

---

## Predictions and Experimental Agreement

| Symbol | Observable | QSD Prediction | Experimental Value | Source | Agreement |
|---|---|---|---|---|---|
| $\alpha^{-1}$ | fine structure constant | 137.0330 | 137.0360 | CODATA 2018 | 22 ppm |
| $\alpha_s$ | strong coupling at $M_Z$ | 0.11781 | 0.1180 | PDG 2022 | 0.16% |
| $\sin^2\theta_W$ | weak mixing angle | 0.23122 | 0.23122 | PDG 2022 | 0.004% |
| $m_H$ | Higgs boson mass | 126.7 GeV | 125.25 GeV | PDG 2022 | 1.2% |
| $m_W$ | W boson mass | 81.1 GeV | 80.377 GeV | PDG 2022 | 0.9% |
| $log(\rho_\Lambda/\rho_{Pl})$ | cosmological constant | −121.28 | −121.27 | Planck 2018 | 0.008% |

Additionally, QSD predicts a **syndrome energy** $E_{syn} \approx 28.2$ GeV — a novel resonance
with no Standard Model counterpart — that corresponds to the dimuon excess observed
by CMS at $\sqrt{s} \approx 28.3$ GeV.

---

## Release Contents

### Manuscripts (9 documents)

| Document | Description | Pages |
|---|---|---|
| **Main Preprint** | Complete framework: postulates → derivations → predictions → experimental tests | ~15 |
| **Supplement S1** | Rigorous formal proofs of all core theorems | ~15 |
| **Supplement S2** | Energy scale derivation: Planck mass $\rightarrow$ electroweak scale via $2^{60}$ compression | ~15 |
| **Supplement S3** | QSD Lagrangian construction from geometric potentials | ~15 |
| **Supplement S4** | 3-loop topological renormalization procedure on $K_4–C_5$ graph | ~10 |
| **Supplement S5** | Syndrome energy prediction (28.2 GeV) and proton lifetime bounds | ~15 |
| **Supplement S6** | Correspondence with string-theoretic constructions | ~15 |
| **Supplement S7** | Cosmological constant from computational thermodynamics | ~10 |
| **Tech Note TN-1** | Holographic bit density $Hb$: notation clarification and redefinition | ~10 |

All documents are provided as both LaTeX source (in `tex/`) and pre-compiled PDF
(in `pdf/`).

### Computational Suite (8 Python modules)

The code implements all QSD computations in a modular architecture where every
module imports physical constants from a single source of truth (`qsd_constants.py`).

**Core modules** (NumPy + SciPy only):
- `qsd_constants.py` — All QSD constants and derived predictions
- `qsd_simulation_suite.py` — Numerical eigenvalue and stabilizer simulations
- `qsd_monte_carlo.py` — Monte Carlo validation of error bounds

**Visualization modules** (+ Matplotlib):
- `qsd_visualizations.py` — Static publication-quality figures
- `qsd_animations.py` — Animated GIF visualizations of QSD mechanisms
- `qsd_syndrome_production.py` — Syndrome energy cross-section analysis

**Quantum circuit modules** (+ Qiskit ≥ 1.0):
- `qsd_qiskit_suite.py` — Nine quantum circuit simulations including $[[5,1,3]]$
  code verification, $K_4 Heisenberg VQE, and stabilizer measurements
- `qsd_qiskit_additions.py` — Extended experiments: Trotter evolution, Mathieu
  equation circuits, advanced VQE

### Interactive Visualizations (3 HTML applications)

Self-contained Three.js web applications (no server required):
- `qsd_4simplex.html` — 4-Simplex geometry explorer
- `qsd_4simplex_network.html` — Tensor network visualization
- `qsd_4simplex_snap_mechanism.html` — Snap mechanism animation

---

## Installation and Reproduction

### Environment Setup

```bash
conda env create -f environment.yml
conda activate qsd
```

### Verify All Predictions

```bash
cd code
python qsd_constants.py
```

This prints every QSD prediction alongside its experimental counterpart, including
error percentages and algebraic identity checks.

### Run Simulations

```bash
python qsd_simulation_suite.py    # Numerical eigenvalue analysis
python qsd_monte_carlo.py         # Monte Carlo validation
python qsd_qiskit_suite.py        # Quantum circuit simulations (requires Qiskit)
```

### Generate Figures

```bash
python qsd_visualizations.py      # Static figures → figures/
python qsd_animations.py          # Animated GIFs → figures/
```

### Compile LaTeX

```bash
make all                           # Builds all PDFs → pdf/
```

---

## System Requirements

- Python ≥ 3.10, NumPy ≥ 1.24, SciPy ≥ 1.10
- Matplotlib ≥ 3.7 (for visualizations)
- Qiskit ≥ 1.0, Qiskit-Aer ≥ 0.13 (optional, for quantum circuits)
- TeX Live 2023+ (optional, for LaTeX compilation — pre-compiled PDFs included)
- Modern web browser (for interactive Three.js visualizations)

---

## Known Limitations

- The fine structure constant prediction (22 ppm error) is the least precise
  among the gauge couplings, pending further investigation.
- Mass predictions for $m_H$ and $m_W$ carry $\sim1\%$ error, suggesting the energy
  scale dressing procedure (Supplement S2) may benefit from refinement.
- The Qiskit modules require Qiskit ≥ 1.0 with the new API; they include
  fallback code for Qiskit-Aer import path changes.

---

## Citation

```bibtex
@misc{hubka2026qsd,
  author  = {Hubka, Marek},
  title   = {Quantum Spectrodynamics: Deriving Standard Model Parameters
             from the Geometry of Quantum Error-Correcting Codes},
  year    = {2026},
  doi     = {10.5281/zenodo.XXXXXXX},
  version = {1.0.0},
  license = {CC-BY-4.0}
}
```

---

## Author

**Marek Hubka**
Independent Researcher, Czech Republic
