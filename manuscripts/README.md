# LaTeX Sources

This directory contains the LaTeX source files for the complete QSD manuscript suite.

## Documents

| File | Document | Description |
|---|---|---|
| `qsd_main_preprint.tex` | **Main Preprint** | Complete framework: postulates, derivations, predictions, and experimental comparisons |
| `qsd_s1_formal_proofs.tex` | **Supplement S1** | Rigorous mathematical proofs for all core theorems |
| `qsd_s2_energy_scale.tex` | **Supplement S2** | Derivation of the electroweak scale from the Planck mass via $2^{60}$ compression |
| `qsd_s3_lagrangian.tex` | **Supplement S3** | Construction of the QSD Lagrangian from geometric potentials |
| `qsd_s4_renormalization.tex` | **Supplement S4** | 3-loop topological renormalization on the $K_4–C_5$ graph |
| `qsd_s5_syndrome_prediction.tex` | **Supplement S5** | Syndrome energy prediction (28.2 GeV) and proton lifetime bounds |
| `qsd_s6_string_correspondence.tex` | **Supplement S6** | Correspondence between QSD and string-theoretic constructions |
| `qsd_s7_cosmological_constant.tex` | **Supplement S7** | Cosmological constant from computational thermodynamics *(speculative extension)* |
| `qsd_tn1_hb_redefinition.tex` | **Technical Note TN-1** | Redefinition and clarification of the holographic bit density $Hb$ |

## Shared Resources

| File | Purpose |
|---|---|
| `qsd_references.bib` | Unified BibTeX bibliography shared by all documents |
| `qsd_preamble.tex` | Unified notation definitions (reference copy — each document currently has self-contained preambles) |

## Compilation

Each document compiles independently. From this directory:

```bash
# Standard LaTeX build cycle
pdflatex qsd_main_preprint.tex
bibtex qsd_main_preprint
pdflatex qsd_main_preprint.tex
pdflatex qsd_main_preprint.tex

# Or use the repository Makefile from the root:
cd .. && make all
```

### Requirements

- TeX Live 2023+ (or MiKTeX / MacTeX equivalent)
- Required packages: `amsmath`, `amssymb`, `amsthm`, `physics`, `tikz`, `hyperref`, `booktabs`, `xcolor`, `geometry`, `graphicx`, `mathtools`
- The `physics` package provides `\bra`, `\ket`, `\braket` notation
- TikZ libraries: `shapes`, `arrows.meta`, `positioning`, `calc`, `decorations.pathmorphing`, `decorations.markings`

## Notation Conventions

The QSD manuscript suite uses a unified notation system:

| Symbol | LaTeX command | Meaning |
|---|---|---|
| $Hb$ | `\Hb` | Holographic bit density |
| $Hb_4$ | `\Hbfour` | $Hb$ in 4 dimensions $= 1/(4 \ln 2)$ |
| $\varsigma$ | `\strain` | Geometric strain $= 3/(80 \varphi^2)$ |
| $\varpi$ | `\specbond` | Spectral bond $= \pi \varphi^2$ |
| $E_{syn}$ | `\Esyn` | Syndrome energy |
| $M_{Pl}$ | `\Mpl` | Planck mass |
| $\mu_0$ | `\murad` | Radiative scale (dimensionful VEV) |
| $\mathscr{L}$ | `\LL` | QSD Lagrangian density |
