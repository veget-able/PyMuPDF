# Painted clip ownership for structured table consumers

- New private collector: src/_table_clip.py, collect(page).
- Missing input supplied: the association between text paint glyphs and the active PDF clip stack, with rectangular background paint order. Ordinary TextPage and line caches do not retain this association.
- Input: already-open, derotated page. Output: call-local glyph IDs, clip scopes, uncertainty events and background paint records. No persistent document cache or global activation.
- Additional page traversal, but no reopening, pixel rendering, OCR, GNN or TGIF. Glyph coordinates represent baseline/advance rather than exact ink bounds.
- Rectangular clip intersection and nested lifetime preserved. Nonrectangular clips and soft masks stay unsupported; masked text is not promoted to affirmative clip evidence. Soft-mask content painting and subsequent mask lifetime handled separately.
- Standalone find_tables behavior unchanged. This module makes no table, span or header decision and has no PyMuPDF4LLM dependency.
- Paired consumer: PyMuPDF4LLM review/table-native-20260923, docs/clip-table-restoration-20261004.md. Existing ruling evidence and producer CellSource references reused there.
- Native tests: actual PDF clip ownership, nonrectangular deferral, mask lifetime and a live soft-mask PDF. Combined products: PB503 GTRM 81.0232% -> 81.3544%, six improving pages and no quality regression; DP200 output unchanged.
- Removal: remove the paired consumer callback first; this otherwise inert collector and setup.py packaging entry can then be removed independently.
