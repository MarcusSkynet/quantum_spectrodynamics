# Release-tree manuscripts/ — documents here use tree-root-relative paths
# (manuscripts/preamble/..., manuscripts/references/...). Compiling with
# cwd = this folder, the '..' element resolves them; the 'references'
# element additionally resolves the main preprint's ../references bib path.
ensure_path('TEXINPUTS', '..');
ensure_path('BIBINPUTS', '..');
ensure_path('BIBINPUTS', 'references');
ensure_path('BSTINPUTS', '..');
$pdf_mode = 1;
