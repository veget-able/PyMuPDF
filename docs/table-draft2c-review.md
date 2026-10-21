# Structured tables on draft 2.0_c

This branch ports the production table functionality onto the exact draft
2.0_c source, rather than installing a 1.28 package over a 2.0 package.

## Review pair

- PyMuPDF: `veget-able/PyMuPDF`, `review/table-draft2c-20261021`.
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
- OCR producer changes remain outside this table review pair. The validation
  run uses the draft's OCR implementation; this distinction is recorded when
  comparing against the previous production deployment's OCR overrides.

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

+-------------------------+-----------+-----------+-----------+
| Configuration           | DL F1 %   | PB F1 %   | PB GTRM % |
+-------------------------+-----------+-----------+-----------+
| Official draft 2.0_c    | 79.571333 | 81.986143 | 75.861747 |
| Previous production     | 81.444918 | 88.864143 | 81.603774 |
| Table port, draft OCR   | 81.499775 | 88.429290 | 80.648183 |
+-------------------------+-----------+-----------+-----------+

For the table port, DL TP/FP/FN is 1815/370/454 (production 1815/373/454),
and PB is 791/105/102 (production 798/105/95). Single-GT F1 is 80.736417%
on DL and 87.646730% on PB, versus 80.682073% and 88.084633% in production.
Single-GT additionally requires exactly one GT owner at >= 50% GT-area coverage;
ineligible predictions remain false positives.

PB GTRM changes are 1 improvement, 9 regressions and 493 unchanged pages.
This table-only branch is therefore NOT claimed to be a regression-free
replacement for the deployed package. CON is 0.8788717596137797 and TRM is
0.7086910229118126. All 6,992 API calls completed, but internal HTML fallback
occurred on 4 PB pages and 8 DL pages; the latter also occurred in production.
API completion is not evidence that every table was successfully reconstructed.

The missing production OCR changes were isolated in a separate diagnostic:

- Distinguishing an empty culling rectangle list from `None` restores the six
  Apple proxy statement pages and their original GNN table boxes.
- Preserving the pre-OCR display list for raster ruling extraction restores
  CA2600. This concerns ruling evidence, not another GNN inference.
- Applying both in an isolated full PB run reproduced production text/HTML
  and raw GNN table boxes on 503/503 pages, with TP/FP/FN 798/105/95 and no
  HTML fallback. This is exact output comparison, not a second official GTRM
  evaluator run. The equivalent DL OCR-controlled run has not been performed.

Neither OCR change is included in this branch. The diagnostic establishes the
PB input-boundary cause; it does not justify attributing the difference to model
weights or claiming general safety. All 18 deployed model files, including
THF1/R6, match the production weights. The native engine differs: draft
MuPDF 1.28.5 versus the deployed 1.29.0.

Validation in the installed review wheel:

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
