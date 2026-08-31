# Derivation Walkthroughs

Complete, step-by-step derivation walkthroughs for the QSD corpus — each
one takes a single result from its axiomatic starting point to the final
number, with every intermediate step written out and machine-verified by a
companion script.

**This directory fills incrementally and independently of the versioned
releases**: a walkthrough is added when it passes review, not when a paper
ships. (Empty at the v2.0 release; the reviewed series lands here one by
one.)

Walkthroughs compile like the supplements — each source carries explicit
relative paths to `../manuscripts/preamble/` and `../manuscripts/references/`, so plain
`pdflatex <walkthrough>.tex` works from this directory. From the
repository root, `make derivations` builds whatever is present.
