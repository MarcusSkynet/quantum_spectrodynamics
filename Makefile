# Quantum Spectrodynamics — Build System
# ========================================
# Compiles all LaTeX sources to PDF.
#
# Usage:
#   make all        Build all PDFs
#   make main       Build main preprint only
#   make supplements Build all supplements
#   make clean      Remove build artifacts
#   make distclean  Remove artifacts + PDFs

TEXDIR  = tex
PDFDIR  = pdf
LATEX   = pdflatex
BIBTEX  = bibtex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error

# Document stems (without .tex extension)
MAIN = qsd_main_preprint
SUPPLEMENTS = qsd_s1_formal_proofs \
              qsd_s2_energy_scale \
              qsd_s3_lagrangian \
              qsd_s4_renormalization \
              qsd_s5_syndrome_prediction \
              qsd_s6_string_correspondence \
              qsd_s7_cosmological_constant
TECHNOTES = qsd_tn1_hb_redefinition

ALL_DOCS = $(MAIN) $(SUPPLEMENTS) $(TECHNOTES)
ALL_PDFS = $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(ALL_DOCS)))

# ── Targets ─────────────────────────────────────────────────

.PHONY: all main supplements technotes clean distclean

all: $(ALL_PDFS)

main: $(PDFDIR)/$(MAIN).pdf

supplements: $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(SUPPLEMENTS)))

technotes: $(addprefix $(PDFDIR)/,$(addsuffix .pdf,$(TECHNOTES)))

# ── Pattern rule: tex → pdf ─────────────────────────────────

$(PDFDIR)/%.pdf: $(TEXDIR)/%.tex $(TEXDIR)/qsd_references.bib | $(PDFDIR)
	@echo "Building $*..."
	cd $(TEXDIR) && $(LATEX) $(LATEXFLAGS) $*.tex
	cd $(TEXDIR) && $(BIBTEX) $* || true
	cd $(TEXDIR) && $(LATEX) $(LATEXFLAGS) $*.tex
	cd $(TEXDIR) && $(LATEX) $(LATEXFLAGS) $*.tex
	mv $(TEXDIR)/$*.pdf $(PDFDIR)/

$(PDFDIR):
	mkdir -p $(PDFDIR)

# ── Cleanup ─────────────────────────────────────────────────

AUXEXT = aux bbl blg log out toc lof lot nav snm vrb fdb_latexmk fls synctex.gz

clean:
	cd $(TEXDIR) && rm -f $(foreach ext,$(AUXEXT),$(addsuffix .$(ext),$(ALL_DOCS)))

distclean: clean
	rm -f $(ALL_PDFS)
