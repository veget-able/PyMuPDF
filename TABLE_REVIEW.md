# Table review branch

Local branch: `review/table-vall-20260917`.
Base: `a2aea0af189911f632168f0ecbff32e70b2de01f` (benchmark source).
No remote push or PR has been performed.

## Scope and review order

1. Virtual line/box forwarding and thin filled rectangle conversion.
2. Repeated leading-header split and 2D text support admission (P1).
3. Bbox/grid provenance and named ruling-evidence collection boundary.
4. Early admission, shared actual edges, spans, drawings and grid operations.
5. HTML-only legacy header omission; public header/Markdown/pandas preserved.
6. Producer-side cell source references and embedded-symbol/glyph geometry.

P1 is replaced at cell-group admission; it is not applied twice. Synthetic
outer edges are retained. Experimental frame suppression and V6 are excluded.
Native/vector/raster source evidence is carried by the existing conversion
path. No new drawing extraction, OCR policy, or blanket TGIF re-execution is
introduced by this packaging.

## Dependencies and limits

This branch is NOT the entire V-all pipeline. The matching PyMuPDF4LLM Table
branch supplies HTML/layout integration. Approved split, recovery and R6
orchestration/model remain in the `pb_table` companion review branch. OCR fixes
are in an independent PyMuPDF4LLM branch. MuPDF/layout native binaries and models
must match the pinned benchmark stack; no C/C++ changes are included here.

The candidate is prepared against the measured source SHA, not veget-able's
current main. A target-base port requires a separate compatibility check.
The companion `docs/table-review-branches-20260917.md` records exact validation,
dependencies and the commit series. Synthetic and glyph tests are provided here;
cross-package producer/consumer and full-503 tests live in the companion repo.
