# Union glyph-statistics reuse

## Scope and implementation

- Performance-only change to the existing union candidate admission stage in src/_table_union.py. Candidate rules, thresholds, dedup order and reconstruction remain unchanged.
- The existing finder CHARS supplies text, centers and vertical extents. No PDF reopening, extraction, OCR or model inference is added.
- _UnionGlyphIntervals prepares valid glyph coordinates once per admission invocation, only if the two-dimensional support rule is reached. Each cell selects the corresponding vertical intervals in the original glyph order.
- Membership remains left/top inclusive and right/bottom exclusive. Python-float center arithmetic precedes float64 array conversion; existing missing-field handling and visual-line counting remain unchanged.
- NumPy is an optional accelerator, not a new PyMuPDF dependency. Without NumPy the same prepared coordinates use scalar membership. The companion PyMuPDF4LLM already depends on NumPy.
- The snapshot is local, not a persistent page/global cache. A new admission invocation reads its current CHARS after OCR/rotation/finder preparation. Direct private support calls create their own snapshot.
- Picture-contained candidate alignment has different validity/line rules and is deliberately unchanged. This patch does not merge the two admission policies.

## Reuse and placement

- The duplicate work was inside the original per-cell character scan, so it is removed there rather than compensated downstream.
- The new private helper serves the existing support function across cells and candidates. It replaces repeated filtering/conversion, not the source of text or the admission rule.
- The standalone HEURISTIC_SPLIT consumer loads this actual product code. Its probe-only dynamic function replacement is not shipped.
- No generic cache framework, spatial tree, ONNX change or public feature flag is introduced. Comparisons still scale with cells times glyphs, with vectorized membership and shared preparation.

## Verification

- Focused tests cover both NumPy and no-NumPy paths: half-open boundaries, empty/invalid glyphs, original order, random membership, scalar-vs-vectorized grid decisions, within-call sharing and cross-call isolation.
- Local A/B artifacts: pb_table/runs/laura-glyph-approval-20261013. Only the union Python module differs between its two runtime packages; compiled MuPDF/Layout, OCR composition and models are reused.
- 220 focused/native/companion tests pass. All three fixed seeds on PB503 and validation156 preserve complete split plans over three paired repetitions per seed.
- Pure splitter mean time: PB 98.890 to 13.055ms (-86.80%); validation 10.693 to 2.311ms (-78.39%). Existing prepared materials exclude PDF/OCR/model work; glyph preparation is included.
- Full API A/B: all 703 PB/DP documents have identical complete chunks. PB503 also exactly matches the currently published raw and normalized output. The fixed 51-document subset has two additional equal-output repetitions.
- Full PB API call-time sum: 584.854 to 559.972 seconds (-4.25%, one complete paired pass). DP200: 137.551 to 137.298 seconds (-0.18%, effectively unchanged). Initialization and serialization are excluded; PDF/OCR/GNN/TGIF/HTML execution is included.
- The repeated PB33 subset averages only -0.57%, with per-repeat direction varying. Full-PB savings are concentrated in some expensive pages; neither 86% end-to-end improvement nor a universal 4.25% gain is claimed.
- API calls alternate A/B; the inactive process is suspended to prevent idle ONNX pools spinning. ONNX product defaults may still use several CPU cores. The splitter uses one CPU; the shared server is not an isolated performance lab.
- Measured details, timing records and limitations are in the run's README and summary.json. Existing compiled binaries and the separately approved OCR composition were reused; no new engine/platform validation is claimed.
