# Quantum Spectrodynamics (QSD)

**A framework for deriving physical dynamics from eigenvalue spectra of quantum error correction codes**.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18832273.svg)](https://doi.org/10.5281/zenodo.18832273)

---

## The question

The universe is suspiciously stable.

An isolated qubit in the best laboratory on Earth decoheres in microseconds.
A warm, dense, radiation-bathed universe has maintained coherent, lawful,
persistent structure for 13.8 billion years — the same particles, the same
couplings, the same interference phenomena, everywhere we look. Quantum
states are fragile; the quantum *universe* is not.

Physics knows exactly one class of systems that preserve quantum information
against continuous noise: **error-corrected** ones. QSD takes that
observation as its single structural axiom:

> **L0.** The universe is a quantum error-correcting code
> $[[n,k,d]]_q$ — with all four parameters initially unknown.

Everything else is derivation. The code parameters are *selected*, not
chosen: a seven-step exclusion chain plus Landauer's thermodynamic principle
single out the perfect five-qubit code $[[5,1,3]]_2$ as the unique
minimal, thermodynamically ground-state solution. The selected code's
geometry then fixes three constants, and those constants fix the dynamics.

**QSD is a framework for deriving physical dynamics — not, specifically, a
model of the Standard Model.** The Standard Model sector (gauge couplings,
masses) is its first worked application (v1.0, this repository's original
release); the same machinery derives the code-selection theorem itself and
gravitational dynamics (Phase 2, releasing incrementally as v2.x).

---

## The triad

The $[[5,1,3]]_2$ code determines two graphs — the complete graph $K_4$
(bulk exchange) and the 5-cycle $C_5$ (geometric clock) — and each
fundamental constant is owned by one substructure, or by their union:

| Constant | Symbol | Expression | Value | Origin |
|---|---|---|---|---|
| Holographic bit density | $\mathrm{Hb}_4$ | $1/(4\ln 2)$ | 0.36067 | $K_4$ — the $n{-}k=4$ stabiliser/face count |
| Spectral bond | $\varpi$ | $\pi\varphi^2$ | 8.22480 | $C_5$ — spectral class ratio $\varphi^2$ |
| Geometric strain | $\varsigma$ | $3/(80\varphi^2)$ | 0.01432 | $K_4 \cup C_5$ — $\beta_1(K_4)$ over Landauer capacity × stiffness |

where $\varphi = (1+\sqrt5)/2$ is the golden ratio. The strain is the only
member that irreducibly mixes both subgraphs — it is the *frustration* of
the two geometries trying to be regular simultaneously, and it is the small
parameter through which the code's mismatch leaks into every observable.
A signature exact identity: in the product $\varsigma\varpi = 3\pi/80$ the
golden ratio cancels — this is the strong coupling.

The famous factor 4 in the Bekenstein–Hawking entropy $S = A/(4\ell_P^2)$
is, in this framework, a *consequence* of $\mathrm{Hb}_4$'s face count —
not an input to it.

### Key predictions vs. experiment

| Symbol | Observable | QSD | Experiment | Source | Agreement |
|---|---|---|---|---|---|
| $\alpha^{-1}$ | Fine structure constant | 137.0330 | 137.0360 | CODATA 2018 | -21.7 ppm |
| $\alpha_s$ | Strong coupling at $M_Z$ | 0.11781 | 0.1180 | PDG 2022 | 0.16% |
| $\sin^2\theta_W$ | Weak mixing angle | 0.23122 | 0.23122 | PDG 2022 | 0.004% |
| $m_H$ | Higgs boson mass | 126.7 GeV | 125.25 GeV | PDG 2022 | 1.2% |
| $m_W$ | W boson mass | 81.1 GeV | 80.377 GeV | PDG 2022 | 0.9% |
| $\log(\rho_\Lambda/\rho_{Pl})$ | Cosmological constant | −121.28 | −121.27 | Planck 2018 | 0.008% |

Zero free parameters beyond the Planck mass (the sole dimensionful input).
The **snap energy** $E_{\mathrm{syn}} = 28.24$ GeV is a novel falsifiable
prediction, coinciding with the dimuon excess reported by CMS at
$\sqrt{s} \approx 28.3$ GeV.

---

## A modular, versioned corpus

The QSD record grows by *parts*: each release adds a self-contained paper
with its supplements and never rewrites published sources (corrections ship
as errata).

| Version | Part | Contents |
|---|---|---|
| **v1.0** | Phase 1 — the Standard Model sector | Main preprint + supplements S1–S7 + TN-1 |
| **v2.0** | Phase 2, Paper 1 — code selection | P1 (the QECC Selection Theorem) + S8 (crossing errors & Deutsch CTCs) + S9 (the observer) |
| v2.1+ | Phase 2, Papers 2–5 (planned) | node & triad → lattice → transition → Einstein equations, each with its supplements |
| v3 | Knowledge base (planned) | the QSD wiki: validated, cross-linked, machine-checked canon |

`manuscripts/derivations/` collects complete step-by-step derivation
walkthroughs as they pass review — these are release-independent and appear
incrementally.

### Epistemic discipline

Every major claim in the Phase 2 papers carries exactly one tag:
**[R]** rigorous (derived from L0 + established mathematics) ·
**[C+]** well-supported conjecture (its external premise is named) ·
**[T]** thermodynamic principle (Landauer/Second Law — empirical, not
axiomatic) · **[EXP]** exploratory · **[O]** open question.
The v1.0 papers used the coarser Derived/Constructed/Open scheme; the
mapping is one-to-one on shared claims.

---

## Repository structure

```
quantum_spectrodynamics/
├── README.md                             This file
├── CITATION.cff                          Machine-readable citation metadata
├── zenodo_meta.md                        Zenodo record description (modular)
├── environment.yml                       Conda environment for all code
├── Makefile                              Build PDFs + release bundles
├── LICENSE                               CC BY 4.0
│
├── manuscripts/                          LaTeX sources
│   ├── quantum_spectrodynamics.tex       Main preprint (v1.0)
│   ├── qsd2_p1_code_selection.tex        Phase 2 Paper 1 (v2.0)
│   ├── supplements/                      S1–S9 + TN-1
│   │   ├── qsd_s1_formal_proofs.tex          S1: Formal proofs
│   │   ├── qsd_s2_energy_scale.tex           S2: Energy scale and dressing
│   │   ├── qsd_s3_lagrangian.tex             S3: The QSD Lagrangian
│   │   ├── qsd_s4_renormalization.tex        S4: Topological renormalization
│   │   ├── qsd_s5_syndrome_prediction.tex    S5: The 28 GeV prediction & proton stability
│   │   ├── qsd_s6_string_correspondence.tex  S6: String correspondence
│   │   ├── qsd_s7_cosmological_constant.tex  S7: Cosmological constant
│   │   ├── qsd2_s8_crossing_ctc.tex          S8: Crossing errors & Deutsch CTCs (v2.0)
│   │   ├── qsd2_s9_observer.tex              S9: The observer (v2.0)
│   │   └── qsd_tn1_hb_redefinition.tex       TN-1: Hb notation (read with the errata)
│   └── derivations/                      Reviewed derivation walkthroughs (incremental)
│
├── preamble/                             Shared LaTeX preambles
│   ├── qsd_preamble.sty                  Unified preamble (Phase 2 documents)
│   └── qsd_preamble.tex                  Legacy v1 preamble (reference)
├── references/
│   └── qsd_references.bib                Unified bibliography (all documents)
├── errata/
│   └── qsd_v1_errata.tex                 v1.0 errata & Phase-2 concordance
│
├── pdf/                                  Pre-compiled PDFs (for immediate reading)
├── code/                                 Python computation & validation suite
│   └── qsd_constants.py                  Single source of truth — reproduces
│                                         every numerical prediction
└── visualizations/                       Interactive 3D visualization (Three.js)
```

All documents carry explicit relative paths to `preamble/` and
`references/`, so plain `pdflatex` works from every source directory.

---

## Quick start

### Read

Start with the two entry manuscripts in [`pdf/`](pdf/):
`quantum_spectrodynamics.pdf` (the framework and the Standard Model sector)
and `qsd2_p1_code_selection.pdf` (why $[[5,1,3]]$ and nothing else). Then
follow the supplements as the text cites them.

### Verify

```bash
conda env create -f environment.yml && conda activate qsd
cd code
python qsd_constants.py          # reproduces every prediction, runs self-checks
python qsd_simulation_suite.py   # full numerical validation
python qsd_qiskit_suite.py       # [[5,1,3]] circuits (requires Qiskit)
```

### Build

```bash
make all          # compile every document into pdf/
make main p1      # just the two entry manuscripts
make supplements  # S1–S9 + TN-1
make errata       # the v1 errata
make release      # dist/: loose entry PDFs + supplements+errata zip + full-repo zip
```

---

## Citation

```bibtex
@misc{Hubka2026QSD,
  author = {Hubka, Marek},
  title  = {Quantum Spectrodynamics},
  year   = {2026},
  howpublished = {Zenodo},
  doi    = {10.5281/zenodo.19162378},
  note   = {DOI:10.5281/zenodo.19162378}
}

```

See [`CITATION.cff`](CITATION.cff) for machine-readable metadata.

## License

Text and figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
You are free to share and adapt this material for any purpose with
attribution.

## Author

**Marek Hubka** — Independent Researcher, Czech Republic

---

*Quantum Spectrodynamics v2.0.0 — July 2026*
