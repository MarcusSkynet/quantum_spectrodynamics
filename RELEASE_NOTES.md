# Release Notes — Quantum Spectrodynamics v1.0

**Release date:** February 2026
**DOI:** 10.5281/zenodo.XXXXXXX

---

## Overview

This is the first public release of Quantum Spectrodynamics (QSD), a theoretical framework that derives Standard Model parameters from the geometry of the `[[5,1,3]]` perfect quantum error-correcting code.

The framework takes four inputs — the holographic bit density Hb₄ = 1/(4 ln 2), the golden ratio φ, the graph strain ς = 3/(80φ²), and the Planck mass — and produces, with zero free parameters:

- **Fine structure constant** α⁻¹ = 137.036 (15 ppm from experiment)
- **Weak mixing angle** sin²θ_W = 0.2312 (0.5% from experiment)
- **Higgs mass** m_H = 126.7 GeV (1.3% from experiment)
- **Syndrome energy** E_syn = 28.24 GeV (0.2% from CMS dimuon excess)

---

## Contents of this release

### Theory (paper/)

| Document | Description |
|---|---|
| `qsd_main_preprint.tex` | Self-contained preprint presenting the full framework |
| `S1_formal_proofs.tex` | Formal proofs: K₄ ground state, C₅ eigenstructure, code properties |
| `S2_energy_scale.tex` | Derivation of the code energy scale μ₀ from M_Pl |
| `S3_lagrangian.tex` | Effective Lagrangian of the radion–Higgs sector |
| `S4_renormalization.tex` | 3-loop renormalization of α⁻¹ (topologically terminated series) |
| `S5_syndrome_prediction.tex` | 28 GeV syndrome prediction, branching ratios, Run 3 falsification |
| `S6_string_correspondence.tex` | Structural correspondence with string theory (conjectural) |
| `S7_cosmological_constant.tex` | Cosmological constant from Landauer's principle (speculative) |

### Technical notes (notes/)

| Document | Description |
|---|---|
| `hb_redefinition.tex` | Reframing the transdimensional constant as holographic bit density Hb_n |

### Computational verification (code/)

| Script | Description |
|---|---|
| `qsd_qiskit_suite.py` | 9 Qiskit quantum circuit simulations with IBM Quantum hardware support |
| `qsd_simulation_suite.py` | Complete NumPy verification of all QSD predictions |
| `qsd_monte_carlo.py` | Monte Carlo uncertainty propagation |
| `qsd_syndrome_production.py` | Syndrome production rate at LHC energies |
| `qsd_visualizations.py` | Static figures for the preprint |
| `qsd_qiskit_visualizations.py` | Quantum circuit diagrams |
| `qsd_animations.py` | Animated visualizations of QSD dynamics |

### Notebooks (notebooks/)

| Notebook | Description |
|---|---|
| `qsd_qiskit_notebook.ipynb` | Interactive notebook: run all 9 simulations on simulator or hardware |

### Reproducibility

| File | Description |
|---|---|
| `environment.yml` | Conda environment specification (Python 3.11 + all dependencies) |

---

## Key features of v1.0

### Theoretical

1. **Complete derivation chain** from `[[5,1,3]]` code geometry to SM observables, with every intermediate step documented.

2. **Dual-route verification** of all predictions: K₄-route (gauge sector) and C₅-route (geometric sector) yield consistent results.

3. **Exact values throughout** — the master relation α⁻¹ × ς = 1.9628744... is never approximated as 2.

4. **Sharp falsification criteria** for LHC Run 3 (S5 §7).

5. **Honest scope delineation** — speculative extensions (S6, S7) are clearly separated from established results.

### Computational

1. **Unified backend system** for Qiskit simulations: switch between local simulator and IBM Quantum hardware with a single function call.

2. **Hardware-ready circuits** with proper transpilation for IBM backends.

3. **NumPy fallbacks** for all calculations — the full prediction table can be verified without Qiskit installed.

4. **Reproducible environment** via conda.

---

## Known limitations

- The preprint (v2.1) still uses some legacy notation (δ for graph strain in places; this will be updated to ς in v1.1).
- The Qiskit suite requires `qiskit >= 1.0` and `qiskit-aer >= 0.13` for local simulation; `qiskit-ibm-runtime >= 0.20` for hardware execution.
- S7 (cosmological constant) is explicitly speculative and should not be cited as an established QSD result.
- The SEMA molecular bond algorithm (mentioned in some technical notes) is not included in this release; it will be released separately after further validation.

---

## Versioning

This project uses semantic versioning:

- **v1.0** — First public release. Core framework, 7 supplements, full code suite.
- **v1.1** (planned) — Complete ς notation update across all documents; additional Qiskit simulations.
- **v2.0** (contingent) — Post-Run-3 update incorporating LHC results.

---

## How to cite

```bibtex
@software{hubka_qsd_2026,
  author       = {Hubka, Marcus},
  title        = {Quantum Spectrodynamics: A Framework for Deriving
                  Standard Model Parameters from Information Geometry},
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0},
  doi          = {10.5281/zenodo.XXXXXXX},
  url          = {https://doi.org/10.5281/zenodo.XXXXXXX}
}
```

---

## License

CC BY 4.0 — Creative Commons Attribution 4.0 International
