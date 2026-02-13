# Quantum Spectrodynamics (QSD)

**A framework for deriving Standard Model parameters from information geometry**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## What is QSD?

Quantum Spectrodynamics derives Standard Model parameters from the geometry of the `[[5,1,3]]` perfect quantum error-correcting code. The code's structure produces two complementary graphs — the complete graph K₄ and the cycle graph C₅ — whose spectral properties, combined with three mathematical constants and the Planck mass, yield particle physics observables with zero free parameters.

### Core results

| Observable | QSD prediction | Experimental value | Accuracy |
|---|---|---|---|
| Fine structure constant α⁻¹ | 137.036 | 137.035999084 | 15 ppm |
| Weak mixing angle sin²θ_W | 0.2312 | 0.23121 ± 0.00004 | 0.5% |
| Higgs mass m_H | 126.7 GeV | 125.25 ± 0.17 GeV | 1.3% |
| Syndrome energy E_syn | 28.24 GeV | ~28.3 GeV (CMS excess) | 0.2% |

### Input constants

The entire framework rests on:

- **Hb₄ = 1/(4 ln 2)** — holographic bit density in 4D (from the Bekenstein–Hawking bound)
- **φ = (1+√5)/2** — golden ratio (eigenvalue ratio of C₅)
- **ς = 3/(80φ²)** — graph strain (from K₄ ∪ C₅ topology)
- **M_Pl** — Planck mass (the only dimensionful input)

No parameters are fitted to data.

---

## Repository structure

```
quantum-spectrodynamics/
│
├── paper/                          # Theory documents (LaTeX)
│   ├── qsd_main_preprint.tex       # Main preprint
│   ├── S1_formal_proofs.tex        # Supplement: formal proofs
│   ├── S2_energy_scale.tex         # Supplement: energy scale derivation
│   ├── S3_lagrangian.tex           # Supplement: effective Lagrangian
│   ├── S4_renormalization.tex      # Supplement: 3-loop renormalization
│   ├── S5_syndrome_prediction.tex  # Supplement: LHC phenomenology
│   ├── S6_string_correspondence.tex# Supplement: string theory dictionary
│   └── S7_cosmological_constant.tex# Supplement: dark energy (speculative)
│
├── notes/                          # Technical notes
│   └── hb_redefinition.tex         # Hb_n notation and conventions
│
├── code/                           # Computational verification
│   ├── qsd_qiskit_suite.py         # Qiskit quantum circuit simulations
│   ├── qsd_simulation_suite.py     # NumPy verification of all predictions
│   ├── qsd_monte_carlo.py          # Monte Carlo error analysis
│   ├── qsd_syndrome_production.py  # Syndrome production rate calculations
│   ├── qsd_visualizations.py       # Static figure generation
│   ├── qsd_qiskit_visualizations.py# Qiskit circuit visualizations
│   └── qsd_animations.py           # Animated visualizations
│
├── notebooks/                      # Interactive notebooks
│   └── qsd_qiskit_notebook.ipynb   # Run all simulations (sim + hardware)
│
├── environment.yml                 # Conda environment (full reproducibility)
├── CITATION.cff                    # Machine-readable citation
├── LICENSE                         # CC BY 4.0
├── RELEASE_NOTES.md                # v1.0 release notes
└── README.md                       # This file
```

---

## Quick start

### 1. Set up the environment

```bash
conda env create -f environment.yml
conda activate qsd
```

### 2. Verify core predictions (no Qiskit required)

```bash
cd code/
python qsd_simulation_suite.py
```

This runs all analytical derivations and prints the prediction table.

### 3. Run quantum circuit simulations

```bash
# Local simulator (default)
python qsd_qiskit_suite.py

# IBM Quantum hardware
python qsd_qiskit_suite.py --hw --backend ibm_brisbane
```

Or use the Jupyter notebook for interactive exploration:

```bash
jupyter lab notebooks/qsd_qiskit_notebook.ipynb
```

### 4. Build the paper (optional)

```bash
cd paper/
pdflatex qsd_main_preprint.tex
bibtex qsd_main_preprint
pdflatex qsd_main_preprint.tex
pdflatex qsd_main_preprint.tex
```

---

## How to read this repository

**If you are a physicist** evaluating the theoretical claims:

1. Start with `paper/qsd_main_preprint.tex` — the self-contained preprint
2. Check `paper/S1_formal_proofs.tex` for derivation rigour
3. Run `code/qsd_simulation_suite.py` to independently verify every number

**If you are a quantum information scientist:**

1. The `[[5,1,3]]` code structure is in the main preprint §2
2. The K₄ Heisenberg exchange model is in `paper/S1_formal_proofs.tex`
3. Qiskit implementations are in `code/qsd_qiskit_suite.py` (9 simulations)

**If you are interested in the LHC prediction:**

1. `paper/S5_syndrome_prediction.tex` — the 28 GeV syndrome prediction
2. Falsification criteria and Run 3 predictions are in S5 §7

**If you are a string theorist:**

1. `paper/S6_string_correspondence.tex` — structural dictionary between QSD and string theory

---

## What is speculative

Honesty about the framework's boundaries:

| Component | Status | Document |
|---|---|---|
| α⁻¹, sin²θ_W, m_H derivations | **Established** — derived, verified | Main preprint, S1, S4 |
| 28 GeV syndrome prediction | **Testable** — awaiting Run 3 | S5 |
| String theory correspondence | **Conjectural** — structural dictionary | S6 |
| Cosmological constant | **Speculative** — Landauer mechanism | S7 |

Supplements S6 and S7 are clearly marked as speculative and do not affect the core predictions.

---

## Falsification

QSD makes falsifiable predictions (see S5 §7 for the full table):

- **Syndrome mass**: 28.24 ± 0.5 GeV → falsified if outside 27–29 GeV
- **Run 3 significance**: ≤ 3–4σ → falsified if it exceeds 5σ (that would indicate a real particle, not a syndrome)
- **Proton lifetime**: > 10³⁸ years → falsified if proton decay is observed
- **Width**: broad/unresolved → falsified if a narrow resonance is measured

---

## Master relation

The framework satisfies an exact constraint linking the fine structure constant to graph strain:

```
α⁻¹ × ς = 1.962874...    (exact, NOT approximated as 2)
```

All code preserves this exact value. The approximation α⁻¹ × ς ≈ 2 is never used.

---

## Citation

If you use this work, please cite:

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

This work is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this material for any purpose, provided you give appropriate credit.

---

## Contact

Marcus Hubka — Independent Researcher, Czech Republic

For questions, corrections, or collaboration proposals, please open an issue in this repository or contact via the email listed in the preprint.
