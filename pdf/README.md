# Pre-Compiled PDFs

This directory contains pre-compiled PDF versions of all QSD documents for immediate reading.

## Reading Order

1. **`qsd_main_preprint.pdf`** — Start here. The main paper presents the complete framework, from the $[[5,1,3]]$ code postulate through gauge coupling derivations to experimental predictions.

2. **Supplements** (consult as needed for detailed derivations):
   - `qsd_s1_formal_proofs.pdf` — Mathematical proofs for all core theorems
   - `qsd_s2_energy_scale.pdf` — How the electroweak scale emerges from the Planck mass
   - `qsd_s3_lagrangian.pdf` — Full Lagrangian construction
   - `qsd_s4_renormalization.pdf` — The 3-loop topological renormalization procedure
   - `qsd_s5_syndrome_prediction.pdf` — The 28.2 GeV syndrome prediction and proton decay
   - `qsd_s6_string_correspondence.pdf` — Correspondence to string theory constructions
   - `qsd_s7_cosmological_constant.pdf` — Cosmological constant problem *(speculative extension)*

3. **Technical Notes:**
   - `qsd_tn1_hb_redefinition.pdf` — Clarification of the $Hb$ notation and redefinition

## Recompilation

These PDFs can be regenerated from the LaTeX sources in `../manuscripts/`:

```bash
cd .. && make all
```

See `../manuscripts/README.md` for compilation requirements.
