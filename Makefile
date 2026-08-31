# Quantum Spectrodynamics — Build System (v2.0 layout)
# =====================================================
# Compiles all LaTeX sources to PDF and builds release bundles.
# Every document carries explicit relative paths to preamble/ and
# references/, so plain `pdflatex` works from each source directory.
#
# Usage:
#   make all          Build every document into pdf/
#   make main         Main preprint only
#   make p1           Phase 2 Paper 1 only
#   make supplements  S1–S9 + TN-1
#   make errata       v1 errata
#   make derivations  Reviewed walkthroughs (as they appear)
#   make release      dist/: entry PDFs + supplements+errata zip + repo zip
#   make clean        Remove build artifacts
#   make distclean    Remove artifacts + PDFs + dist/

VERSION = 2.0
MANDIR  = manuscripts
SUPDIR  = manuscripts/supplements
DERDIR  = manuscripts/derivations
ERRDIR  = errata
PDFDIR  = pdf
DISTDIR = dist
LATEX   = pdflatex
BIBTEX  = bibtex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error

# Document stems (without .tex extension)
MAIN        = quantum_spectrodynamics
P1          = qsd2_p1_code_selection
SUPPLEMENTS = qsd_s1_formal_proofs \
              qsd_s2_energy_scale \
              qsd_s3_lagrangian \
              qsd_s4_renormalization \
              qsd_s5_syndrome_prediction \
              qsd_s6_string_correspondence \
              qsd_s7_cosmological_constant \
              qsd2_s8_crossing_ctc \
              qsd2_s9_observer \
              qsd_tn1_hb_redefinition
ERRATA      = qsd_v1_errata
DERIVATIONS = $(basename $(notdir $(wildcard $(DERDIR)/*.tex)))

ALL_PDFS = $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(MAIN) $(P1) $(SUPPLEMENTS) $(ERRATA) $(DERIVATIONS)))

# ── Targets ─────────────────────────────────────────────────

.PHONY: all main p1 supplements errata derivations release clean distclean

all: $(ALL_PDFS)

main: $(PDFDIR)/$(MAIN).pdf

p1: $(PDFDIR)/$(P1).pdf

supplements: $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(SUPPLEMENTS)))

errata: $(PDFDIR)/$(ERRATA).pdf

derivations: $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(DERIVATIONS)))

# ── Build rules ─────────────────────────────────────────────

define COMPILE
	@echo "Building $(2) (in $(1))..."
	cd $(1) && $(LATEX) $(LATEXFLAGS) $(2).tex
	cd $(1) && $(BIBTEX) $(2) || true
	cd $(1) && $(LATEX) $(LATEXFLAGS) $(2).tex
	cd $(1) && $(LATEX) $(LATEXFLAGS) $(2).tex
	@mkdir -p $(PDFDIR)
	mv $(1)/$(2).pdf $(PDFDIR)/
endef

$(PDFDIR)/$(MAIN).pdf: $(MANDIR)/$(MAIN).tex references/qsd_references.bib
	$(call COMPILE,$(MANDIR),$(MAIN))

$(PDFDIR)/$(P1).pdf: $(MANDIR)/$(P1).tex references/qsd_references.bib preamble/qsd_preamble.sty
	$(call COMPILE,$(MANDIR),$(P1))

$(PDFDIR)/$(ERRATA).pdf: $(ERRDIR)/$(ERRATA).tex references/qsd_references.bib preamble/qsd_preamble.sty
	$(call COMPILE,$(ERRDIR),$(ERRATA))

$(PDFDIR)/%.pdf: $(SUPDIR)/%.tex references/qsd_references.bib
	$(call COMPILE,$(SUPDIR),$*)

$(PDFDIR)/%.pdf: $(DERDIR)/%.tex references/qsd_references.bib
	$(call COMPILE,$(DERDIR),$*)

# ── Release bundles (Zenodo file set) ───────────────────────
# Loose entry PDFs + supplements(+errata) zip + full-repo snapshot zip.
# The full zip uses `git archive` and therefore contains the committed tree.

release: all
	@mkdir -p $(DISTDIR)
	cp $(PDFDIR)/$(MAIN).pdf $(PDFDIR)/$(P1).pdf $(DISTDIR)/
	cd $(PDFDIR) && zip -q ../$(DISTDIR)/qsd_v$(VERSION)_supplements.zip \
		$(addsuffix .pdf,$(SUPPLEMENTS) $(ERRATA))
	git archive --format=zip --prefix=quantum_spectrodynamics/ \
		-o $(DISTDIR)/qsd_v$(VERSION)_full.zip HEAD \
		|| echo "NOTE: commit the tree first — the full zip archives HEAD."
	@echo "Release bundle in $(DISTDIR)/:" && ls -l $(DISTDIR)

# ── Cleanup ─────────────────────────────────────────────────

AUXEXT = aux bbl blg log out toc lof lot nav snm vrb fdb_latexmk fls synctex.gz

clean:
	cd $(MANDIR) && rm -f $(foreach ext,$(AUXEXT),*.$(ext))
	cd $(SUPDIR) && rm -f $(foreach ext,$(AUXEXT),*.$(ext))
	cd $(ERRDIR) && rm -f $(foreach ext,$(AUXEXT),*.$(ext))
	-cd $(DERDIR) && rm -f $(foreach ext,$(AUXEXT),*.$(ext))

distclean: clean
	rm -f $(ALL_PDFS)
	rm -rf $(DISTDIR)
