# Supplements use tree-root-relative paths (manuscripts/preamble/...);
# from this folder the tree root is two levels up.
ensure_path('TEXINPUTS', '../..');
ensure_path('BIBINPUTS', '../..');
ensure_path('BSTINPUTS', '../..');
$pdf_mode = 1;
