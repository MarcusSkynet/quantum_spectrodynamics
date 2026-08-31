# Supplements (S1–S9) and Technical Notes

The supplement series is **programme-wide**: S1–S7 belong to the Phase 1
release (v1.0), S8+ to the Phase 2 releases (v2.x). Each supplement is
self-contained and compiles independently.

| File | Document | Release | Description |
|---|---|---|---|
| `qsd_s1_formal_proofs.tex` | **S1** | v1.0 | Rigorous proofs of all algebraic results ($K_4$ spectrum, $S_4$ representation theory, $C_5$ Laplacian, master theorems) |
| `qsd_s2_energy_scale.tex` | **S2** | v1.0 | The electroweak scale from the Planck mass via the $2^{60}$ compression |
| `qsd_s3_lagrangian.tex` | **S3** | v1.0 | The QSD Lagrangian (field-theoretic formulation) |
| `qsd_s4_renormalization.tex` | **S4** | v1.0 | 3-loop topological renormalization on the $K_4$–$C_5$ graph ($\alpha^{-1} = 137.033$) |
| `qsd_s5_syndrome_prediction.tex` | **S5** | v1.0 | The 28.24 GeV snap-energy prediction and proton stability |
| `qsd_s6_string_correspondence.tex` | **S6** | v1.0 | Correspondence with string-theoretic constructions *(exploratory)* |
| `qsd_s7_cosmological_constant.tex` | **S7** | v1.0 | Cosmological constant from computational thermodynamics *(conjecture, premise named)* |
| `qsd2_s8_crossing_ctc.tex` | **S8** | v2.0 | Crossing errors and Deutsch CTCs: the crossing-error channel as a closed timelike curve, fixed-point consistency, forensic record |
| `qsd2_s9_observer.tex` | **S9** | v2.0 | The observer as code-internal structure; measurement as syndrome extraction |
| `qsd_tn1_hb_redefinition.tex` | **TN-1** | v1.0 | The $Hb$ notation ($\mathcal{T}$ retired, $\mathrm{Hb}_n$ family). *Read with the v1 errata: its "$K_4$-route strain" and the printed $\alpha^{-1}_{\text{tree}}$ closed form are corrected there.* |

Published sources stay frozen; corrections ship in the v1 errata
(distributed with the v2.0 release).

## Compilation

From the repository root: `make supplements`. By hand, plain `pdflatex`
works from this directory — every source carries explicit relative paths
to `../../preamble/` and `../../references/`:

```bash
pdflatex qsd2_s8_crossing_ctc.tex
bibtex   qsd2_s8_crossing_ctc
pdflatex qsd2_s8_crossing_ctc.tex
pdflatex qsd2_s8_crossing_ctc.tex
```
