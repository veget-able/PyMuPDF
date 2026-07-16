# Upstream proposal: layout-aware table refinement in PyMuPDF core, with pymupdf4llm as a thin consumer

Audience: PyMuPDF maintainers (Harald, Robin) and pymupdf4llm maintainers.
Status: two coupled PRs, ready for review. Measured on ParseBench (LlamaIndex),
`table` group, 503 pages / 284 documents, `concurrent=1`, metric GTRM.

> [!NOTE]
> **Review branches (single squashed commit each, based on the respective
> upstream mains):**
> - PyMuPDF: `single-diff/table-refine-html` @ https://github.com/veget-able/PyMuPDF
>   (commit `e91ae6b3`, +3,805/−74 across 8 files; no C changes)
> - pymupdf4llm: `single-diff/html-tables-v2` @
>   https://github.com/veget-able/pymupdf4llm (commit `44db965`, +907/−53)
>
> Since this document's section bodies were first written, the header-semantics
> rule engine and the HTML serializer were **also moved into PyMuPDF core**
> (`_table_headers.py`; `find_tables(refine=True)` now yields header-tagged
> merged-cell placements + `header_rows`/`stub_cols`/`section_rows` meta, and
> `Table.to_html()` mirrors the existing `to_markdown()`/`to_pandas()`
> presentation methods). pymupdf4llm's `helpers/table_html` is now a **178-line
> thin consumer** (payload assembly + a standalone `to_html` convenience). The
> core serializer was proven byte-identical to the previous engine output
> (191/191 tables) and the full benchmark re-verified at GTRM 72.11 after the
> move. Line counts / file lists in the PR sections below that predate this
> move should be read against the review branches, which are authoritative.

All API names, signatures, test names, commit hashes, and line references below
were verified against the current branch state, not the design notes.

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [PR 1 — PyMuPDF (`src/table.py`)](#2-pr-1--pymupdf-srctablepy)
3. [PR 2 — pymupdf4llm](#3-pr-2--pymupdf4llm)
4. [Bug reports](#4-bug-reports)
5. [TableFinder / TableHunter position](#5-tablefinder--tablehunter-position)
6. [Measurement appendix](#6-measurement-appendix)

---

## 1. Executive summary

Two changes, submitted as two PRs:

- **PR 1 — PyMuPDF core (`src/table.py` only).** One correctness fix and three
  opt-in extensions to `find_tables()`. The correctness fix (per-call character
  snapshot, `ContextVar`-isolated state) stops a stale-text bug that already
  exists in released 1.28.0. The extensions — a `use_layout=` opt-out, a
  `refine=` grid refiner (row/column splitters + `resolve_spans`), and a
  `use_layout=True, union=` layout∪line-candidate fuser — are all **off by
  default**; the default detection path is unchanged.
- **PR 2 — pymupdf4llm.** A `table_output="html"` opt-in on `to_markdown` /
  `to_json`, backed by a table-to-HTML engine that is now a thin consumer of the
  PR-1 core APIs: it delegates detection, grid refinement, and span resolution to
  `pymupdf.table` and keeps only header tagging and rendering. Removes the fork's
  `bs4`/`lxml` additions.

**Headline numbers (503 pages, GTRM):**

| | GTRM | GriTS-con | TRM | TRM-perfect |
|---|---:|---:|---:|---:|
| Official 1.28.0 baseline | 56.73 | 0.7257 | 0.3791 | 0.2252 |
| This proposal | **72.11** | 0.8134 | 0.6053 | 0.4497 |

Plus: a deterministic correctness fix (stale-CHARS re-extraction), and measured
byte-for-byte neutrality for users who do not opt in.

**Coupling between the two PRs.** PR 2 hard-depends on PR 1: the engine calls
`pymupdf.table.refine_grid_structure` / `refine_grid_rows` / `resolve_spans` and
`page.find_tables(use_layout=True, union=True)`. If PR 2 lands without PR 1, the
`to_markdown(..., table_output="html")` / `to_json` opt-in path **degrades
gracefully** — the per-page engine call raises, is caught in
`document_layout.parse_document` (a logged warning, not a silent swallow), and the
page falls back to the standard layout/markdown table path (GNN grid → markdown).
Non-opt-in users (`table_output="markdown"`, the default) are unaffected in
either case. The standalone helper `table_html.to_html()` is the one surface that
requires PR 1 outright (it calls `find_tables(union=True)` unguarded). The two
PRs should therefore land together.

---

## 2. PR 1 — PyMuPDF (`src/table.py`)

> Branch: `minsu/find-tables-use-layout`. Scope: `src/table.py` and
> `tests/test_tables.py` only. Base: official 1.28.0.

### 2.1 Summary

Adds one correctness fix and three opt-in capabilities to `find_tables()`, all
gated so the default result is unchanged:

- **Correctness:** per-call character/edge state isolation (`ContextVar`) and a
  per-table character snapshot, fixing a stale-text bug in released 1.28.0.
- **`use_layout=` opt-out** (default `True` = current behavior).
- **`refine=`** — opt-in grid refinement (row/column splitters) and cell-span
  resolution, exposing `Table.placements` and a new `SpanCell` type.
- **`use_layout=True, union=`** — opt-in fusion of the layout analyzer's GNN
  table grids with the line-based finder's candidates. Reads
  `page.layout_information` raw groups directly and is the proper replacement for
  the broken `make_table_from_bbox` path (see §4.2).

### 2.2 Correctness: `ContextVar` isolation + per-call chars snapshot

Released 1.28.0 keeps the detector's working character and edge lists in two
process-global module lists (`CHARS`, `EDGES`) and has `Table.extract()` read the
live `CHARS` list lazily. A second `find_tables()` call clears `CHARS` before the
first call's tables are re-extracted, so the first tables then extract **wrong
text** (see bug report §4.1).

This PR:

- Backs the module-level `CHARS` / `EDGES` with `ContextVar`s
  (`_CHARS_VAR`, `_EDGES_VAR`, `default=None`) through a small list-like proxy
  (`_TableStateList`). State becomes per-call and per-context, so concurrent
  `find_tables()` calls in different threads/contexts no longer share one list.
- Snapshots the characters once per call at the end of `find_tables()` and
  attaches the snapshot to every returned table:
  `chars = list(CHARS); for table in tbf.tables: table._chars = chars`. One
  shallow copy per call, no re-scan.
- Has `Table.extract()` prefer that snapshot:
  `chars = self._chars if self._chars is not None else CHARS`. A later call's
  `CHARS` reset can no longer leak into an earlier table's extraction.
- Hot-loop micro-opt: `make_chars` / `make_edges` bind the underlying list once
  (`CHARS._list()` / `EDGES._list()`) instead of paying proxy dispatch on each of
  ~20 appends.

Regression test: `test_table_extract_stable_after_second_find_tables`.
Thread/context safety test: `test_find_tables_state_is_call_local_for_threads`.

### 2.3 `find_tables(use_layout=)` opt-out

Released 1.28.0 calls `page.get_layout()` **unconditionally** inside
`find_tables()` and gates line-based detection by the layout table boxes (when
the layout wheel is present), with no way to opt out. This PR wraps that logic in
`if use_layout:` with:

```python
def find_tables(page, ..., use_layout: bool = True, union: bool = False, refine: bool = False):
```

- `use_layout=True` (default) — **identical to current behavior**: consult
  `get_layout()`, restrict/complete line-based detection with the layout table
  boxes, return empty if layout ran and found no tables.
- `use_layout=False` — skip `get_layout()` entirely; run full line-based
  detection. This is what the pymupdf4llm engine's nested candidate detection and
  the union path need, and it restores pre-layout-gating behavior for any caller
  that wants it.

Test: `test_find_tables_use_layout_false_does_not_call_get_layout`;
`test_find_tables_use_layout_true_without_layout_is_line_based`.

### 2.4 Opt-in `refine=` (grid splitters + span resolution)

`refine=True` post-processes each detected table before the `Table` is built:
`refine_grid()` splits rows/columns the ruling-line grid merged (using page text
and background shading), then `resolve_spans()` resolves the merged-cell
structure and is attached as `Table.placements`. Off by default — the standard
detection result and `extract()` / `to_markdown` output are unchanged.

New public functions on `pymupdf.table` (verified signatures):

```python
def refine_grid_structure(page, cells, *, table_bbox=None)                       # shaded-row + under-segmented-column split
def refine_grid_rows(page, cells, *, header_row_count=1,
                     clean_threshold=0.85, merge_overlap_frac=0.35)              # body-row overmerge split
def refine_grid(page, cells, *, table_bbox=None, header_row_count=1)            # all-in-one wrapper of the two above
def resolve_spans(page, cells, *, header_row_count=None, strict_colspan=False)  # -> row-major grid of SpanCell
```

The structural half and the row half are exposed **separately** on purpose: a
caller that must know the header/body boundary of the *post-structure* grid (the
pymupdf4llm engine's header resolver runs between the two phases) inserts that
computation between `refine_grid_structure` and `refine_grid_rows`. `refine_grid`
is the convenience wrapper for callers that do not.

New type:

```python
class SpanCell:                        # one reconstructed cell after span resolution
    bbox, text, colspan, rowspan       # HTML td/th tagging is deliberately the caller's concern
```

`Table` gains `Table.placements` (a row-major grid of `SpanCell`; `None` on the
default path, filled only by `refine=True`).

Tests: `test_refine_grid_splits_overmerged_body`,
`test_find_tables_refine_splits_rows_default_unchanged`,
`test_resolve_spans_merged_header`,
`test_find_tables_refine_exposes_placements_default_none`.

### 2.5 Opt-in `use_layout=True, union=`

`union=True` (requires the layout analyzer) fuses two table sources on the page:

- **Primary grids** from the layout analyzer — each `"table"` group in
  `page.get_layout(return_raw=True)` carries a `GridPrediction` whose interior
  `h_lines`/`v_lines` are turned into a full row-major cell grid
  (`_layout_table_grids`).
- **Candidate grids** from a nested pure `find_tables(strategy="lines_strict",
  use_layout=False)`.

Reconciliation is contractual (the pymupdf4llm engine keys tables by output
order): a candidate matching a primary 1:1 by IoU may **replace** its grid
(grid-ref); candidates each contained in one primary may **split** it; unowned
candidates are **appended**; output order is primary order then appended order.
`Table` gains an optional reported-bbox override (`Table._bbox`, set only for a
grid-ref table whose reported region — the layout box it stands in for — is
decoupled from its replacement grid).

`_layout_table_grids` reads `page.layout_information` in its raw form directly.
It is also **the correct replacement for the `make_table_from_bbox` path**
(§4.2): that path expects a `FZ_STEXT_BLOCK_GRID` block the current MuPDF stext
walker never emits, so it silently yields `[]`. The union path does not depend on
it.

Tests: `test_find_tables_union_fuses_layout_grid_with_line_candidate`,
`test_find_tables_union_no_layout_degrades_to_line_candidates`.

### 2.6 Defaults untouched (neutrality, measured)

| Check | Result |
|---|---|
| Plain `to_markdown` (default `table_output`), 20 PDFs, md5 | byte-identical 20/20 |
| `find_tables` default path, no-layout wheel, 50 pages | output byte-identical, **+1.0%** time |
| Default path with GNN wheel present | no systematic overhead (interleaved measurement) |

The `+1.0%` is the `ContextVar`/proxy overhead on the no-layout path; output is
unchanged. `refine`, `union` default `False`; `use_layout` defaults `True`
(current behavior).

### 2.7 New public API surface on `pymupdf.table`

| Symbol | Kind | Default-path effect |
|---|---|---|
| `find_tables(..., use_layout=True)` | opt-out param | none (True = current) |
| `find_tables(..., refine=False)` | opt-in param | none |
| `find_tables(..., union=False)` | opt-in param | none |
| `refine_grid_structure` / `refine_grid_rows` / `refine_grid` | functions | new |
| `resolve_spans` | function | new |
| `SpanCell` | class | new |
| `Table.placements` | attribute | `None` unless `refine=True` |

### 2.8 Tests

New tests in `tests/test_tables.py` (verified present, absent from the 1.28.0
base):

```
test_find_tables_use_layout_false_does_not_call_get_layout
test_find_tables_use_layout_true_without_layout_is_line_based
test_find_tables_state_is_call_local_for_threads
test_table_extract_stable_after_second_find_tables
test_refine_grid_splits_overmerged_body
test_find_tables_refine_splits_rows_default_unchanged
test_find_tables_refine_exposes_placements_default_none
test_resolve_spans_merged_header
test_find_tables_union_fuses_layout_grid_with_line_candidate
test_find_tables_union_no_layout_degrades_to_line_candidates
```

### 2.9 Commits

`git log --oneline` since the 1.28.0 base (`e9cdfc9e`):

```
186d415f  tests: cover refine_grid, resolve_spans, and union find_tables
80212c76  table.py: opt-in grid refinement, span resolution, and layout union
ac1432da  tests: stale-CHARS extract stability and layout-absent use_layout
9d314d69  table.py: reduce proxy overhead, document use_layout and chars snapshot
63660f09  test: cover find_tables use_layout state
1f4a359a  add find_tables(use_layout=) opt-out ("chloe update p1")
```

(`1f4a359a` introduces the `use_layout` opt-out; the four commits above it add the
chars snapshot / proxy work, the refine/span/union APIs, and their tests. Squash
to taste for submission.)

---

## 3. PR 2 — pymupdf4llm

> Branch: `fix/table-output-layout-wiring`. **Note:** the final delegation cleanup
> is currently in the working tree, not yet committed (see §3.9).

### 3.1 Summary

- `table_output="html"` opt-in on `to_markdown` / `to_json` (default stays
  `"markdown"`).
- The table-to-HTML engine becomes a **single-representation** engine
  (`TableModel`) and a **thin consumer** of PR-1 core APIs: detection, grid
  refinement, and span resolution are delegated to `pymupdf.table`; the engine
  keeps only header tagging and one-pass HTML rendering.
- `to_json` gains html-mode grid fields (`row_count`/`col_count`/`cells`/
  `extract`) describing the reconstructed grid.
- Removes the fork's `bs4`/`lxml` dependencies.
- Byte-level neutrality for non-opt-in users.

### 3.2 `table_output="html"` opt-in

`to_markdown(..., table_output="markdown" | "html")` (default `"markdown"`;
validated — anything else raises `ValueError`). In HTML mode the engine, not
`page.find_tables()`, is the source of the page's tables and drives emission,
reading order, and body-text exclusion. The same opt-in flows through `to_json`.
The engine is imported lazily, only when `table_output="html"` is requested.

### 3.3 `TableModel` single-representation engine

Before, the only integrated per-table representation was the HTML string, which
the pipeline re-parsed (regex round-trips) to recover structure. Now a first-class
model carries everything once:

```python
@dataclass(frozen=True)
class CellPlacement:                       # wraps a core pymupdf.table.SpanCell + HTML tag
    text; colspan; rowspan; bbox=None; tag="td"

@dataclass(frozen=True)
class TableModel:
    rows; row_count; col_count
    top_header_rows=0; left_stub_cols=0; section_header_rows=()
```

Detection/refinement delegation (the coupling to PR 1):

| Engine step | Delegates to (PR 1) |
|---|---|
| page detection + layout∪line union | `page.find_tables(use_layout=True, union=True)` |
| structural grid split | `pymupdf.table.refine_grid_structure(...)` |
| body-row split (given header boundary) | `pymupdf.table.refine_grid_rows(..., header_row_count=...)` |
| cell-span resolution | `pymupdf.table.resolve_spans(..., strict_colspan=..., header_row_count=...)` |

The engine reconstruct step calls `refine_grid_structure`, computes the
header/body boundary on the post-structure grid, then calls `refine_grid_rows` —
using the two-phase core seam exactly for that ordering. Header tagging
(`td`/`th`) runs on the `TableModel` itself (no HTML re-parse), and `renderer.py`
serializes the model to `<table>` HTML in a single pass.

### 3.4 `to_json` html-mode grid fields

In HTML mode the reconstructed grid — not the GNN layout grid or a best-fit
rematch — is authoritative, so each table box's JSON carries:

```
row_count, col_count   # the post-split working grid actually serialized
cells                  # post-span cell-bbox matrix (None for span-covered slots / gaps)
extract                # parallel plain-text matrix (None likewise)
markdown = None        # html is authoritative in this mode
html                   # the emitted <table>
```

These describe the *same* grid the `html` shows (`RenderedTable`), which can
differ from the raw engine grid after row/column splitting.

### 3.5 Dependency removal (`bs4`/`lxml`)

The former render→reparse→retag round-trip pulled in `bs4`/`lxml` (fork
additions). Header tagging now runs on the model and rendering is direct string
assembly (`core.escape_html_text`, byte-identical to the old escaping), so both
are removed. **No `bs4`/`lxml`/`BeautifulSoup` remain in the engine source.**
`tabulate` is an *official* pymupdf4llm dependency (used by `to_text`) and is
retained; only the fork's additions are dropped.

Public surface is a single knob: `table_output="html"`. The former public
`render_html_tables` is now an internal `parse_document` parameter; the engine
package exports only `to_html` and `page_html_tables`.

### 3.6 Neutrality (byte-level, non-opt-in users)

| Check | Result |
|---|---|
| `to_markdown` default (`table_output="markdown"`), 20 PDFs, md5 | byte-identical 20/20 |
| `to_json` / `to_markdown` HTML-mode value equivalence | equal (not merely existential) |

### 3.7 Benchmark impact

503-page ParseBench `table`, GTRM: the wired engine reaches **72.11** (baseline
56.73). See §6.

### 3.8 Tests

`tests/test_table_html.py`:

```
test_to_html_is_live_only_public_api
test_page_html_tables_uses_core_union_find_tables
test_to_markdown_table_output_html_uses_layout_path
test_to_json_table_output_html_uses_layout_path
test_to_json_html_tables_match_to_markdown
test_to_json_html_mode_grid_fields_consistent
test_table_output_html_no_layout_falls_back_to_rag_path
test_body_text_preserved_around_tables
test_layout_html_env_does_not_enable_table_html
test_table_html_parallel_smoke
```

### 3.9 Commits

Substantive commits on `fix/table-output-layout-wiring` (earliest first;
scaffolding/merge commits omitted). The final delegation cleanup (deleting the
experimental `candidates.py`, trimming `reconstruct.py` / tests) is **currently
uncommitted in the working tree** and must be committed before the PR is opened:

```
97d2515  feat(rag): add table_output="html" to to_markdown
c574fdc  table_html: re-vendor production engine to 5-module structure
43401b2  render table_html engine on the layout path, reusing the GNN
ebeb80c  route table_output="html" through the layout path (keep OCR + layout text)
49f6875  thread-lock for multi-thread concurrent
7478787  reading order, thread-safe lock, wire to to_json, opt-in
ac70292  remove serialized find_tables guard
7a75efb  strip research scaffolding, dedup hot path, clean API
114405c  tests: parity, fallback, body-text coverage
890c733  table_html: delegate detection and refinement to pymupdf core
70a37aa  tests: track core delegation and model-based engine
(uncommitted)  drop candidates.py, trim reconstruct/tests to the delegated engine
```

Recommend squashing to a small, reviewable set before submission.

---

## 4. Bug reports

### 4.1 Stale characters after a second `find_tables()` call

- **Summary.** After `page.find_tables()`, re-extracting a returned table's text
  can return the wrong text if another `find_tables()` (on any page) has run in
  between. The detector keeps its working character list in a process-global
  module list (`CHARS`) and `Table.extract()` reads it lazily; the second call
  clears `CHARS` before the first call's tables are re-extracted.
- **Affected versions.** Released 1.28.0 (`src/table.py`: `Table.extract()` reads
  the module-global `CHARS`; `find_tables()` resets it at entry).
- **Repro.** Deterministic test
  `test_table_extract_stable_after_second_find_tables` (find tables on page A,
  find tables on page B, re-extract page A's table → wrong text on the released
  build; correct with the fix).
- **Suggested fix.** Snapshot the character list once per `find_tables()` call and
  attach it to each returned `Table`; have `extract()` prefer that snapshot over
  the live global. Optionally back the module lists with `ContextVar` for
  thread/context isolation. (Both implemented in PR 1 §2.2.)

### 4.2 `make_table_from_bbox` type mismatch (silent empty tables)

- **Summary.** `pymupdf.table.make_table_from_bbox` → `extra.make_table_dict`
  (`fz_find_table_within_bounds`) is the existing Python entry point for
  bbox-bounded table detection. `make_table_dict` fills its result only when the
  returned block is `FZ_STEXT_BLOCK_GRID` (type 4), but on current MuPDF builds
  `fz_find_table_within_bounds` returns a Table **STRUCT** block
  (`FZ_STEXT_BLOCK_STRUCT`, type 2). The `== FZ_STEXT_BLOCK_GRID` check is never
  true, so `make_table_dict` returns `{}` and `make_table_from_bbox` returns `[]`
  — always, silently (no exception, no signal). On the default `use_layout=True`
  path this appends **empty `Table`s** for layout table boxes the line finder did
  not match.
- **Affected versions.** Released 1.28.0 (`src/table.py: make_table_from_bbox`,
  the `FZ_STEXT_BLOCK_GRID` check, and its call site on the `use_layout` path;
  `src/extra.i: make_table_dict`, the `block->type == FZ_STEXT_BLOCK_GRID` guard).
  A scan across 40 ParseBench PDFs found 0/36 finder-bbox trials ever produced a
  grid through this path.
- **Repro.** `tablehunter-comparison/repro_make_table_from_bbox_bug.py` (prints
  `make_table_from_bbox(...) -> 0 cells` while a table is genuinely present, and
  `raw fz_find_table_within_bounds(...) block.type = 2`).
- **Suggested fix.** Reconcile the type check with what the detector returns
  today: either have the detector populate a `FZ_STEXT_BLOCK_GRID`-shaped result
  the wrapper expects, or update `make_table_dict` / `make_table_from_bbox` to
  read the `STRUCT` block and expose its already-computed per-cut uncertainty at
  the Python level (which would also unblock the cell-merge work in §5). PR 1
  sidesteps this on the union path by building grids from the GNN
  `GridPrediction` directly (`_layout_table_grids`), but the broken wrapper is
  still live on the default `use_layout` path and should be fixed or retired.

### 4.3 `get_tessdata()` subprocess breaks on non-UTF-8 Windows locales (noisy, per-call cost)

- **Summary.** `pymupdf.get_tessdata()` probes tesseract by spawning a
  subprocess (`tesseract --list-langs`). On Windows systems with a non-UTF-8
  ANSI code page (e.g. Korean cp949), the subprocess's localized output is not
  valid UTF-8; when the parent runs in UTF-8 mode (`PYTHONUTF8=1`, increasingly
  the default in tooling), the stdlib pipe-reader threads crash with
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0/0xc1 ...`
  ("Exception in thread Thread-N (_readerthread)") on **every call**. The probe
  result is effectively lost, so tesseract is treated as unavailable — silently.
  The function is also called per document on hot paths: pymupdf4llm's layout
  pipeline reaches it via `select_ocr_function` whenever `use_ocr=True` (the
  library default) with no `ocr_function` supplied, and we measured a ~70 ms
  floor per probe (two subprocess spawns), up to ~350 ms/page when a caller
  probes per request.
- **Affected versions.** Released 1.28.0 (`pymupdf.get_tessdata()`); any
  non-UTF-8 Windows locale; surfaced through pymupdf4llm's default
  `use_ocr=True` path and any caller that probes eagerly.
- **Repro.** Korean-locale Windows, `PYTHONUTF8=1`,
  `python -c "import pymupdf; pymupdf.get_tessdata()"` with a tesseract binary
  whose localized output is cp949 (or absent, with a localized shell error) —
  reader-thread tracebacks appear on stderr and the call yields no tessdata.
- **Suggested fix.** Run the probe subprocess with an explicit
  `encoding="utf-8", errors="replace"` (or capture bytes and decode
  defensively) so locale output can never kill the reader threads, and cache
  the probe result process-wide so the subprocess cost is paid at most once
  instead of per call/page.

### 4.4 `cells_to_tables()` text probe rebuilds a TextPage per candidate (module-global `TEXTPAGE` never assigned)

- **Summary.** `cells_to_tables()`'s "remove tables without text" filter calls
  `page.get_textbox(r, textpage=TEXTPAGE)` with the module-global `TEXTPAGE` —
  but nothing ever assigns that global. Its comment ("textpage for cell text
  extraction") and the `TEXTPAGE = make_chars(...)` binding in `find_tables()`
  suggest the sharing was intended and a `global` statement was lost at some
  point; as written, `make_chars()` and `find_tables()` only bind locals of the
  same name, so the probe always receives `textpage=None`. `get_textbox()` then
  builds a fresh full-page TextPage **and Python-walks every character of it**
  (`JM_copy_rectangle`) — once per candidate table. Measured on ParseBench's
  table corpus: ~24 ms per probe, ~30% of `find_tables()` wall time — the
  largest single cost after character extraction, spent re-deriving information
  that is already sitting in `CHARS` at that point.
- **Affected versions.** Released 1.28.0 (`src/table.py`: module global
  `TEXTPAGE = None`; the whitespace filter in `cells_to_tables()`). The same
  never-assigned global is present on current upstream main.
- **Fix (implemented and measured).** Probe the call's existing `CHARS` instead:
  same strict-overlap rule as `JM_rects_overlap()`, same whitespace-only
  rejection, built lazily only when a candidate survives the geometric checks —
  and drop the dead global. One commit, `src/table.py` only (+27/−8):
  https://github.com/veget-able/PyMuPDF/commit/35c633ce7c54f71796b20226c699c0cd6a88068f
  Across all 503 benchmark pages the produced tables are hash-identical
  (bbox + cells, 636 tables) and GTRM is unchanged at 72.11 to four decimals;
  `find_tables()` mean wall time drops 106.1 → 75.9 ms/page (−28%).
- **Why not just pass the TextPage through.** Threading `make_chars()`'s
  TextPage into the probe restores the apparent original intent but recovers
  almost nothing (−0.7% measured): `extractTextbox` itself Python-walks every
  character of the page per call (~22 ms), so the cost is the walk, not the
  build. The `CHARS` scan removes both.

---

## 5. TableFinder / TableHunter position

**Position: keep `TableFinder` (`page.find_tables`) as the default/primary
detector for now.** The union role in PR 1 needs `TableFinder`'s ruling-line-exact
grids; MuPDF's native detector recovers table *regions* well but over-segments the
*grid*.

Data (from `tablehunter-comparison/`, and the 503-page benchmark):

| | Finder (`page.find_tables`, `lines_strict`) | TableHunter (`fz_find_table_within_bounds`, GNN-box-bounded) |
|---|---|---|
| Region recovery given a GNN box | reference | **22/22 recovered**, IoU 0.87–1.00 |
| Region recovery, whole-page `fz_table_hunt` | — | **0/22** on those same cases |
| Grid cell count on recovered regions | reference (ruling-line-exact) | **4.1×–15.7×** more cells (over-segmentation) |
| GTRM as union candidate source, 503p | **72.11** | **52.06** (−20.1) |
| `make_table_from_bbox` wrapper | n/a | broken (§4.2) |

Over-segmentation gallery (finder cells → hunter TDs): 16→251 (15.7×), 15→105
(7.0×), 12→103 (8.6×), 14→108 (7.7×), 22→91 (4.1×) — with mid-sentence and even
mid-word splits ("Depar" / "rtment"). Even an exact bbox match (IoU 1.00) still
over-segments.

**Mechanism.** The detector *does* consume ruling lines
(`TABLE_DETECTOR_FLAGS` includes `TEXT_COLLECT_VECTORS`), but its segmentation is
uncertainty-scored, not ruling-line-gated — every candidate cut becomes a real TD
boundary in the `stext` output; and `stext` `TD` elements carry no
rowspan/colspan, so a real spanned cell cannot round-trip.

**Constructive ask (to close the gap and make TableHunter a drop-in detector):**

1. **Ruling-line-authoritative segmentation** — when `TEXT_COLLECT_VECTORS` finds a
   (near-)complete ruling grid inside the bounds, snap segmentation to those lines
   as ground truth and fall back to uncertainty-based cuts only where no line
   exists. This alone should collapse most extra TDs on ruled tables.
2. **Uncertainty-keyed cell merge** — the detector already computes a per-cut
   uncertainty; use it to merge TDs across low-confidence internal cuts.
3. **rowspan/colspan on `TD`** (or an adjacency side-channel) so merged source
   cells round-trip.
4. **Fix §4.2** as a low-effort first step, exposing the per-cut uncertainty to
   Python so downstream consumers can do (2) without new MuPDF-side computation.

Reproducible comparison package: `tablehunter-comparison/`
(`compare_finder_hunter.py`, `repro_make_table_from_bbox_bug.py`, and the
`examples/` grid-pair gallery).

**Addendum (2026-07-16, after the raft question).** A fair challenge to this
position is whether the finder earns its runtime when a cheaper region source —
e.g. rafts, connected clusters of overlapping vector bboxes — could stand in
for it. Two measurements say that trade is not available. First, the finder's
contribution to the union is its *cells*, not its boxes: the union adopts
candidate grids (grid-ref / split / append), and in a ground-truth
decomposition, swapping our detection for GT boxes moves GTRM by only ~+0.5
while swapping the reconstructed structure for GT moves it by +13.8–15.5.
Region coverage was never the gap (22/22 above); cell structure is. Second,
the finder's runtime was not where it looked: border geometry (intersections +
cell assembly) is ~2% of `find_tables()` wall time, and the dominant cost
turned out to be the accidental per-candidate TextPage rebuild of §4.4. With
§4.4 fixed (−28%), what remains is character extraction and per-table header
detection — content work any text-emitting detector pays in some form. A raft
prefilter could therefore only shave the ~2% geometry slice, and rafts as the
bbox source would forfeit the grids that carry the score. Rafts inside the
hunt's own region proposal are, as we understand 1.28's hunter, already the
direction MuPDF has taken; the remaining gap for this role is grid
segmentation — asks (1)–(3) above.

---

## 6. Measurement appendix

**Methodology.** ParseBench (LlamaIndex) `table` group, 503 pages / 284
documents, `concurrent=1`. GTRM = the mean of GriTS and TableRecordMatch
structural-match scores. GTRM is reported ×100 in the headline (72.11) and as a
0–1 fraction in the tables below (0.7211); they are the same number.

### 6.1 GTRM progression

| Stage | GTRM |
|---|---:|
| Official 1.28.0 baseline | 0.5673 (56.73) |
| Fork installed, `table_output="html"` not passed (opt-in inactive) | 0.5673 — identical to baseline; the feature is strictly opt-in |
| Wired (`table_output="html"`), pre-refactor | 0.7206 |
| Final (this proposal) | **0.7211 (72.11)** |

Sub-metrics, baseline → final: GriTS-con 0.7257 → 0.8134; TRM 0.3791 → 0.6053;
TRM-perfect 0.2252 → 0.4497.

### 6.2 Ablation (503p; each row removes one stage from the full pipeline)

| Configuration | GTRM | Δ vs full |
|---|---:|---:|
| Full pipeline (finder + union + refine) | 0.7211 | — |
| − union (grid-ref −3.8 / append −3.8) | 0.6449 | −7.6 |
| − grid-ref only | 0.6827 | −3.8 |
| − splitters | 0.6520 | −6.9 |
| − spans | 0.6715 | −5.0 |
| − header tagging | 0.6559 | −6.5 |
| TableHunter as union source (finder replaced) | 0.5206 | −20.1 |
| No-layout engine (finder-only, no GNN) | 0.4034 | below baseline |
| No-layout, splitters+spans off | 0.3065 | −9.7 vs no-layout engine |

Reading: all four stages now live in core (see the note at the top) — union
(+7.6), splitters (+6.9), spans (+5.0), and header tagging (+6.5, which keys on
TRM). Without the GNN layout, recall collapses (0.4034 < 0.5673 baseline) — but
there the refinement stages matter *more*, not less (splitters+spans worth +9.7).

### 6.3 Neutrality

| Check | Result |
|---|---|
| Plain `to_markdown` (default `table_output`), 20 PDFs | byte-identical 20/20 |
| `find_tables` default path, no-layout wheel, 50 pages | byte-identical output, +1.0% time |
| Default path with GNN wheel present | no systematic overhead (interleaved) |
