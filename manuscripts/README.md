# LaTeX Sources

This directory holds the two **entry manuscripts** plus the shared LaTeX
infrastructure; the supplement series lives in
[`supplements/`](supplements/) and reviewed derivation walkthroughs appear
incrementally in [`derivations/`](derivations/).

## Entry manuscripts

| File | Document | Release | Description |
|---|---|---|---|
| `quantum_spectrodynamics.tex` | **Main Preprint** | v1.0 | Complete framework: postulates, derivations, predictions, and experimental comparisons (Standard Model sector) |
| `qsd2_p1_code_selection.tex` | **Phase 2 — Paper 1** | v2.0 | The QECC Selection Theorem: why $[[5,1,3]]$ and nothing else — the seven-step exclusion chain from L0 plus Landauer's principle |

## Shared infrastructure (repository-level)

| Location | Purpose |
|---|---|
| `references/qsd_references.bib` | **Unified bibliography** — one BibTeX file for every document in the corpus (v1 + v2) |
| `preamble/qsd_preamble.sty` | **Unified preamble** — notation, palette, epistemic marks; loaded by the Phase 2 documents |
| `preamble/qsd_preamble.tex` | Legacy v1 preamble (reference copy — the v1 documents carry self-contained preambles) |
| `errata/qsd_v1_errata.tex` | v1.0 errata & Phase-2 concordance (ships with v2.0) |

Every document references these by **explicit relative path**
(e.g. `\bibliography{references/qsd_references}`), so no environment
variables are needed.

## Compilation

Each document compiles independently. From the repository root:

```bash
make main p1      # the two entry manuscripts
make all          # everything, into ../pdf/
```

Or by hand from this directory:

```bash
pdflatex quantum_spectrodynamics.tex
bibtex quantum_spectrodynamics
pdflatex quantum_spectrodynamics.tex
pdflatex quantum_spectrodynamics.tex
```

### Requirements

- TeX Live 2023+ (or MiKTeX / MacTeX equivalent)
- Packages: `amsmath`, `amssymb`, `amsthm`, `physics`, `tikz`, `hyperref`,
  `booktabs`, `xcolor`, `geometry`, `graphicx`, `mathtools`, `mdframed`
- TikZ libraries: `shapes`, `arrows.meta`, `positioning`, `calc`,
  `decorations.pathmorphing`, `decorations.markings`

## Notation conventions

| Symbol | LaTeX command | Meaning |
|---|---|---|
| $Hb$ | `\Hb` | Holographic bit density |
| $Hb_4$ | `\Hbfour` | $Hb$ in 4 dimensions $= 1/(4 \ln 2)$ — K₄-owned |
| $\varsigma$ | `\gs` (alias `\strain`) | Geometric strain $= 3/(80 \varphi^2)$ — K₄∪C₅ |
| $\varpi$ | `\specbond` | Spectral bond $= \pi \varphi^2$ — C₅-owned |
| $E_{syn}$ | `\Esyn` | Snap (syndrome) energy |
| $M_{Pl}$ | `\Mpl` | Planck mass |
| $\mu_0$ | `\murad` | Radion VEV (dimensionful) |
| $\mathscr{L}$ | `\LL` | QSD Lagrangian density |

Phase 2 documents additionally carry the epistemic tags
$[R]$ / $[C+]$ / $[T]$ / $[EXP]$ / $[O]$ on every major claim.
