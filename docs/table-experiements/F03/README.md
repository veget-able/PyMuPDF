# F03: Recover the painted axis of wide short strokes

Status: implemented-evaluated. Production and Viewer are unchanged.

## Implemented behavior

Convert supported single solid butt-capped short strokes using their painted axis before minimum-length filtering and clipping. Main already contains thin-fill recovery; it is retained without copying the production table.py wholesale.

## Source and dependencies

Branch: table-experiements/f03-vector-rule-recovery
Evaluated source commit: 422dadaf42a39d1c5acf93b0026a2cbdbc00f7b4
Paired PyMuPDF: 422dadaf42a39d1c5acf93b0026a2cbdbc00f7b4
Paired pymupdf4llm: 363f177ef50deb05f07db8bf2061e7b9c8102b07
Baseline: the frozen main pair in manifest.json. This is not the existing production stack.
No full-tree overlay or pb_table policy adapter is used. Source bytes are checked against Git.
Python sources use the pinned official draft 2.0_c native bindings/models. Native main was not rebuilt.

## Validation

Focused tests: 9 passed. Public to_markdown / parse_document+serializer parity: 3 pages.
Automatic OCR, original full pages, fixed RF+IMF1 weights, ORT/BLAS one thread.
bbox: IoU >= 0.60 one-to-one; single-GT is reported separately.
GTRM: original production ParseBench scorer source, unchanged normalization and metrics.
Selection: CURRENT v12 r5, 998 pages, 2735 bbox GT; key_value included, exclude_for_detection ignored.
Selection visible-text and per-cell evaluation contracts are preserved: 992 GTRM pages, 2724 tables.

Full actual API evaluation: PB503 + DL6489 + Selection998, 7,990 successful page runs for this variant.
All improved/regressed and score-neutral changed pages are in evaluation-20261029/*.tsv; full identities and before/after metrics are in the compressed ledgers.
PB verdicts (any metric or bbox count/GT identity): {'improved': 0, 'regressed': 0}.
DL verdicts (bbox count/GT identity): {'improved': 0, 'regressed': 0}.
Selection verdicts: {'improved': 0, 'regressed': 0, 'output_only': 0}.
A page can be both improved and regressed when components or GT identities differ.
Empty-GT pages with new FP are regressions even if their page F1 remains zero.

## Limits and reproduction

This is measured development-corpus behavior, not independent generalization or automatic adoption.
Main does not expose raw GNN or CellSource in this public payload. Lexical deltas are diagnostics, not proof of glyph loss or preservation.
Shared CPU concurrent evaluation is not a controlled runtime A/B; no feature speed claim is made.
Local runner: scripts/analysis/run_feature_ports_20261029.py (prepare, inventory, run, score).
Selection runner: scripts/analysis/evaluate_feature_selection_20261029.py.
Page comparison: scripts/analysis/summarize_feature_ports_20261029.py.
Exact source/model/scorer/data hashes are included in evaluation-contract.json; full local raw evidence: runs/laura-feature-ports-20261029/.
Continue code and evidence commits on this branch; do not replace it with a new revision branch.
