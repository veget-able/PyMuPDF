# Private structured-table consumer boundary

For the September 24 follow-up (stroke geometry and candidate admission), see
[the consolidated review bundle](table-regression-fixes-20260924.md). Its PB
scores remain equal but three PB outputs change, and its DP detection improves.
The integration-only parity results below are historical, not final-bundle
output parity claims.

Scope note (2026-09-24): the unchanged-standalone statement below describes the
September 23 integration only. The subsequent `stroke-rule-geometry` fix changes
standalone output on three BLS pages. See `docs/table-features.md` section 3.2.1
for its separate API regression results and limits.

This review change supplies the missing native integration points for the
paired PyMuPDF4LLM HTML table pipeline. It adds no PyMuPDF4LLM/ONNX dependency to
PyMuPDF and leaves standalone finder/layout behavior unchanged when no consumer
is active. The companion product owns the table algorithms and R6 model.

`_table_pipeline.activate(runtime)` is a private, context-local scope, not a
public plugin API. It dispatches existing layout prediction, union selection,
header-band refinement and final-role construction to one document's consumer.
Original implementations remain the default and are directly reused by the
consumer. Nested activation is rejected and scope cleanup is exception-safe.

The change preserves existing source/geometry/ruling caches and table producer
references. It does not replace line detection, introduce another GNN call,
modify OCR, or change union thresholds. The companion consumer serializes HTML
calls because native geometry state remains process-global.

`setup.py` now includes `_table_pipeline.py` and the previously omitted
`_table_word_geometry.py`/`_table_font_symbols.py` in wheels. Those latter two
algorithms already belonged to the September 17 reviewed Table source; only
their packaging omission is fixed here.

Verification with the paired products and separately composed reviewed OCR:
503/503 raw and normalized outputs equal the September 17 composition;
GTRM `0.8098682258124252`, GriTS_CON `0.8856166354231998`, TRM
`0.7091856091907063`. Four local boundary/packaging tests plus 155 companion
tests pass. Existing compiled MuPDF/Layout were reused, not rebuilt; no claim
is made for a new engine or arbitrary upstream model version.

See the companion repository's `docs/native-table-pipeline.md` for the public
usage, feature map, model/OCR dependencies and complete validation limits.
The older `docs/table-features.md` remains the frozen feature specification;
its references to externally activated PB adapters are superseded by this
native wiring, not additional algorithm changes.
