# Structured tables on draft 2.0_c

This branch ports the production table functionality onto the exact draft
2.0_c source, rather than installing a 1.28 package over a 2.0 package.

## Review pair

- PyMuPDF: veget-able/PyMuPDF, 2.0-draft-c-table-20261021.
- PyMuPDF4LLM: `veget-able/pymupdf4llm`, the same branch name.
- Bases: PyMuPDF `7db0ab090698d49de637046786c8f85f29d89fd2` and
  PyMuPDF4LLM `d9b212b737dd27550401a2691a5bc1719b2fef2c`.

These are two source repositories for one integrated wheel, not alternative
implementations. The older `review/table-native-20260923` pair is not required
on top of this pair. No PR is created by the implementation agent.

## Functional scope

1. Ruling evidence and admission: reuse converted vector/raster edges, retain
   narrow filled rules, preserve native versus synthetic provenance, and decide
   independent table creation at the unowned union-append branch. Cell-grid
   supply and replacement remain separate authorities from new-region creation.
2. Region and cell reconstruction: deferred TGIF inference, supported region
   splits, cell-preserving partitioning, repeated leading headers, parent
   coherence checks and ownership-preserving content restoration. Existing
   parent input and prediction results are reused; no new layout model is trained.
3. Final header roles: bundled THF1/R6 ONNX, the frozen 19-feature contract,
   continuous prefix decoding, title input alignment, leaf-label completion,
   unit/section demotion, year rows and the final missing-value cap. Children
   whose grids change are classified after reconstruction.
4. Source-backed content: cells carry their original word/glyph references,
   clipped painted content and supported symbols are restored during cell
   production, and unresolved content retains its ownership information.
5. HTML and reading order: final table metadata and bbox/grid provenance travel
   with the emitted HTML. Tables inside pictures survive layout normalization;
   picture text excludes only glyphs actually owned by emitted table cells.
6. Shared work: page-state drawing and word indexes, stable placement matrices,
   lazy legacy header calculation, shared R6 characters and deferred inference.
   The 2.0 `Table.header` property remains lazy and publicly accessible.

The native table hooks do not import the higher-level consumer. The HTML
consumer installs a call-local runtime; model sessions are shared without
patching the original model object. Native geometry flags are restored on exit.

## 2.0 integration decisions

- Keep shared extraction and reconstruction primitives, with explicit native
  versus structured-consumer policy dispatch. Native 2.0 union admission and
  repeated-header ordering remain available through direct `find_tables()`;
  the HTML runtime selects production admission and refinement ordering.
  Neither policy is installed by global monkeypatching.
- The production HTML path owns its refinement and final R6 ordering. Native
  refinement retains the 2.0 leaf-label completion when no consumer is active.
- Share drawings across the HTML call, while preserving 2.0's call-local cache
  for direct native calls. Consumers receive copies of mutable drawing members.
- Use the same word-center index implementation with the appropriate input-state
  lifetime; cell claiming and original word order are not changed.
- Use source-owned picture text exclusion, not a second bbox-based removal pass.
- Keep the 2.0 native extension/wrapper set together. The old native binaries
  are not copied into this package.
- The header contract is self-contained: it imports neither ParseBench nor
  `pb_table`. `rapidfuzz>=3` is a declared runtime dependency.
- Include two OCR/table input-boundary fixes in the paired 4LLM source:
  distinguish an empty text-culling list from None, and preserve pre-OCR
  rendering for raster ruling detection. The latter leaves live OCR/GNN input
  unchanged and invalidates stale raster-line results in both OCR callbacks.

## Build and validation

For normal builds, follow the draft's build instructions and point
`PYMUPDF_SETUP_PATH_4LLM` to the matching 4LLM checkout. The main PyMuPDF wheel
packages both namespaces, the table runtime modules and the bundled ONNX file.
The 4LLM repository is not built as a separate implementation wheel in 2.0.

`scripts/build_table_review_wheel.py` provides a Python-source review build on
the pinned official Linux x86_64 draft wheel. It preserves the native binaries,
replaces tracked Python sources, includes the model and rewrites wheel RECORD.
This is not a claim that MuPDF/native extensions were recompiled.

Run the focused table tests with `--noconftest` when testing an already installed
wheel, so upstream test setup does not rebuild or install into that environment.
The evaluation data is not part of the wheel.

## Measured review results

The comparison uses the same PDF/GT manifests: PB 503 pages / 893 table boxes
and official DocLayNet validation 6,489 pages / 2,269 table boxes, including
pages without tables. Bbox F1 is micro F1 with IoU >= 0.60 and greedy one-to-one
matching on final HTML table boxes. It is not COCO mAP, a TF/CROSS16 experiment,
or an average over training seeds. The stricter single-GT result is separate.

+----------------------+-----------+-----------+-----------+
| Configuration        | DL F1 %   | PB F1 %   | PB GTRM % |
+----------------------+-----------+-----------+-----------+
| Official draft 2.0_c | 79.571333 | 81.986143 | 75.861747 |
| Current production   | 81.444918 | 88.864143 | 81.603774 |
| Port before A+B      | 81.499775 | 88.429290 | 80.648183 |
| This branch with A+B | 81.444918 | 88.864143 | 81.603774 |
+----------------------+-----------+-----------+-----------+

The A+B combination restores DL TP/FP/FN 1815/373/454 and PB 798/105/95,
exactly matching current production. Single-GT F1 is 80.682073% on DL and
88.084633% on PB, also matching production. Single-GT additionally requires
exactly one GT owner at >=50% GT-area coverage; ineligible predictions remain FP.

The branch includes these two input-boundary fixes in the paired 4LLM checkout:
- An empty culling rectangle list preserves all text for OCR; None retains the
  full-page text-culling default. This restores six Apple proxy-statement pages.
- Both OCR callbacks preserve the first pre-OCR display list for raster ruling
  extraction and invalidate stale raster-line cache entries. Live OCR text,
  layout/GNN inputs and cell-text inputs are not replaced with pre-OCR content.
  This restores CA2600 and ruling-derived cell structures on BRWS pages.

The exact combined sources completed full PB503 and DL6489 execution. PB was
freshly rescored with the official evaluator: GTRM 0.8160377388360863,
CON 0.8898730100285182, TRM 0.7168015922849151, all pagewise identical to
production. DL bbox, HTML, full text and raw GNN tables are identical on
6489/6489 pages; matched GT gains/losses are zero. API failures are zero.
PB has no HTML fallback; the same eight DL fallback pages remain. API success
does not mean those eight pages have successful HTML structure reconstruction.

Against the port before A+B, five old FP predictions return and two port-only
FP predictions disappear (net FP +3). Visual review of the returned predictions
finds one figure-panel grid, one GUI form and three real tables inside screenshots
without matching Table annotations. Existing false positives, incomplete table
extents and annotation-policy differences are not claimed to be resolved.

All 18 deployed model files, including THF1/R6, match production. Layout uses
RF + IMF1; the included IMF2 file is not selected. The native engine remains
draft MuPDF 1.28.5 versus deployed 1.29.0. There is no model or table-rule change
in A+B.

A+B delivery verification:

- The installed review wheel passes 338 selected tests, including eight new
  empty-list/None and pre-OCR pixel/cache regression cases.
- All 157 frozen package files match the full-evaluated A+B composition.
- Public API output on 21 affected/control pages (14 PB and seven DL) exactly
  matches that composition in a clean installation without ParseBench or
  pb_table imports. Both boundary fixes are installed source, not runtime
  diagnostic overrides. No additional model, rule or threshold change is made.
- Full PB/DL results above are reused from the identical measured composition;
  this delivery verification is not presented as another 6992-page rerun.

Original table-only delivery validation (before A+B):

- The final frozen source reruns all 6,992 pages. API/HTML/bbox outputs exactly
  match the first integration run on 6,992/6,992 pages. Bbox scores are recomputed;
  the PB official evaluator report is reused only after this equality check,
  rather than described as a second official evaluator execution.
- 334 focused product tests and 27 selected upstream 2.0 API contract tests pass.
- Public API outputs match on five reconstruction/OCR/span smoke pages, in an
  isolated installation where ParseBench and `pb_table` cannot be imported.
- Standalone title alignment matches the frozen contract on 15,000 synthetic
  grids, including 474 with nonzero alignment offsets.
- Clean Git checkouts rebuild the same 263 wheel file contents as the measured
  working sources. ZIP metadata differs; whole-wheel byte identity is not claimed.
- Validation covers the pinned Linux x86_64 wheel. Native recompilation, other
  platforms and downstream CF/SF/VG performance are not certified by these tests.

The immutable evaluation artifacts are indexed by
`20261021-draft2c-port-final` under the production experiment archive. Detailed
scoring contracts and results are also recorded in the integration workspace's
`docs/experiments/draft2c-production-port-validation-20261021.txt`.

The A+B full-evaluation archives are 20261021-draft2c-ocr-boundary/both
(PB503 official rescore) and 20261021-draft2c-ab-dl-full (DL6489).
The installed delivery wheel, tests and 21-page API comparison are in
20261021-draft2c-ab-delivery. Integration-workspace report:
docs/experiments/draft2c-ab-dl-full-validation-20261021.txt.
