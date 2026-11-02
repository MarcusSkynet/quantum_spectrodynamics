# Pre-Compiled PDFs

Pre-compiled PDF versions of the QSD documents, for immediate reading, in one
folder per release (`v1-0/`, `v2-0/`).

## Reading order

1. **`v1-0/quantum_spectrodynamics.pdf`** — start here. The complete framework,
   from the error-correction axiom through gauge-coupling derivations to
   experimental predictions (v1.0).

2. **`v2-0/qsd2_p1_code_selection.pdf`** — the v2.0 entry document. Why
   $[[5,1,3]]$ and nothing else: the seven-step selection chain plus
   Landauer's thermodynamic principle. Read it, S8 and S9 through the
   errata of the v2.0 set (item 4).

3. **Supplements** (consult as the main texts cite them):
   - `v1-0/qsd_s1_formal_proofs.pdf` — proofs of all core theorems
   - `v1-0/qsd_s2_energy_scale.pdf` — the electroweak scale from the Planck mass
   - `v1-0/qsd_s3_lagrangian.pdf` — full Lagrangian construction
   - `v1-0/qsd_s4_renormalization.pdf` — 3-loop topological renormalization
   - `v1-0/qsd_s5_syndrome_prediction.pdf` — the 28.24 GeV prediction and proton stability
   - `v1-0/qsd_s6_string_correspondence.pdf` — string-theory correspondence *(exploratory)*
   - `v1-0/qsd_s7_cosmological_constant.pdf` — cosmological constant *(conjecture)*
   - `v2-0/qsd2_s8_crossing_ctc.pdf` — crossing errors and Deutsch CTCs (v2.0)
   - `v2-0/qsd2_s9_observer.pdf` — the observer (v2.0)

4. **Technical notes and errata:**
   - TN-1, the $Hb$ notation (read with the v1 errata) — no PDF here; its source is
     `../supplements/qsd_tn1_hb_redefinition.tex`
   - `v1-0/qsd_v1_errata.pdf` — v1.0 errata & Phase-2 concordance
   - `v2-0/qsd_v2_errata.pdf` — errata of the v2.0 set, Revision 2 (release v2.0.1):
     corrects P1, S8 and S9 claim by claim and lists the revisions owed to the v1 errata

Release bundles (`qsd_v2.0_supplements.zip`, `qsd_v2.0_full.zip`) are built
by `make release` into `dist/` and uploaded to Zenodo — they are not
tracked here.

## Recompilation

```bash
cd .. && make all
```

See `../manuscripts/README.md` for compilation requirements.
