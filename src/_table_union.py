"""
Copyright (C) 2023 Artifex Software, Inc.

This file is part of PyMuPDF.

PyMuPDF is free software: you can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

PyMuPDF is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with MuPDF. If not, see <https://www.gnu.org/licenses/agpl-3.0.en.html>

Alternative licensing terms are available from the licensor.
For commercial licensing, see <https://www.artifex.com/> or contact
Artifex Software, Inc., 39 Mesa Street, Suite 108A, San Francisco,
CA 94129, USA, for further information.

---------------------------------------------------------------------

PyMuPDF table union stage (opt-in extension).

Split out of pymupdf/table.py. Provides _find_tables_union and the _union_* /
_layout_table_grids helpers behind find_tables(union=True), which fuse the
layout analyzer's GNN grids with the line-based finder's candidates. Table,
TableFinder and _iou come from pymupdf.table; find_tables is imported lazily
(see _union_line_candidates) to avoid an import cycle.
"""

import os

import pymupdf

from pymupdf.table import CHARS, EDGES, Table, TableFinder, _iou


# ---------------------------------------------------------------------------
# Table union stage (opt-in PyMuPDF extension)
#
# find_tables(union=True) fuses two table sources on one page:
#   * PRIMARY grids from the layout analyzer -- each "table" group returned by
#     page.get_layout(return_raw=True) carries a GridPrediction whose h_lines/
#     v_lines are turned into a full row-major cell grid (_layout_table_grids).
#   * CANDIDATE grids from the line-based finder -- a nested pure find_tables
#     (strategy="lines_strict", use_layout=False).
# and reconciles them: a candidate matching a primary 1:1 (high IoU) may REPLACE
# the primary's grid (grid-ref), a set of candidates each contained in one
# primary may SPLIT it, and candidates owned by no primary are APPENDED. Output
# ordering -- primary order (each kept / grid-ref'd / split) then appended
# candidates -- is contractual: the pymupdf4llm HTML-table engine keys tables by
# it. Migrated from that engine (helpers/table_html/find_tables.py); the engine
# now calls this instead of reimplementing the fusion, and the thresholds below
# are its production StageOptions values.
#
# _layout_table_grids is also the correct replacement for the make_table_from_bbox
# path in find_tables' use_layout branch: make_table_from_bbox ->
# extra.make_table_dict expects an FZ_STEXT_BLOCK_GRID block that the current
# MuPDF stext walker does not emit, so it silently yields [] (an empty Table).
# The GNN GridPrediction is the working grid source. make_table_from_bbox is left
# in place pending a separate cleanup; the union path does not depend on it.
# ---------------------------------------------------------------------------
_UNION_STRATEGY = "lines_strict"          # candidate detection strategy
_UNION_GRID_REF_IOU = 0.9                 # min IoU for a 1:1 grid-ref replacement
_UNION_GRID_REF_SPAN_MULT_GATE = True     # reject under-segmented candidate grids
_UNION_GRID_REF_SPAN_MULT_THRESHOLD = 3.0  # max horizontally-separated span groups per cell
_UNION_OWNER_CONTAINMENT = 0.85           # min containment for a split candidate's owner
_UNION_OWNER_AMBIGUOUS_OVERLAP = 0.25     # overlap above which an unowned candidate is suppressed


def _layout_table_grids(page):
    """Primary table grids from the raw layout analyzer result.

    Reads page.layout_information in its raw (return_raw=True) form -- a list of
    group dicts, each with a "group_bbox", a "class_name" and, for tables, a
    "table_grid" GridPrediction (interior h_lines/v_lines offsets). Each "table"
    group becomes a ``(bbox, grid)`` pair: ``grid`` is the full row-major cell
    grid built from the group box plus the interior grid lines. Ports the grid
    conversion of the pymupdf4llm engine's document_layout.get_table_details;
    tables are yielded in layout (reading) order, reproducing that engine's
    identity box<->grid matching. Boxes without a usable grid are skipped.
    """
    grids = []
    for group in (page.layout_information or []):
        if not isinstance(group, dict):
            # The union path needs the raw (return_raw=True) layout form; the
            # normalized [x0, y0, x1, y1, class] tuples carry no table_grid.
            continue
        if group.get("class_name") != "table":
            continue
        group_bbox = group.get("group_bbox")
        grid_pred = group.get("table_grid")
        if not group_bbox or grid_pred is None:
            continue
        x0, y0, x1, y1 = group_bbox[0], group_bbox[1], group_bbox[2], group_bbox[3]
        h_lines = [y0] + [h + y0 for h in grid_pred.h_lines] + [y1]
        v_lines = [x0] + [v + x0 for v in grid_pred.v_lines] + [x1]
        grid = []
        for i in range(len(h_lines) - 1):
            row = []
            for j in range(len(v_lines) - 1):
                row.append((v_lines[j], h_lines[i], v_lines[j + 1], h_lines[i + 1]))
            grid.append(row)
        grids.append((pymupdf.Rect(group_bbox[:4]), grid))
    return grids


def _union_line_candidates(page):
    """Line-based table candidates for the union stage as ``(bbox, grid)`` pairs.

    Runs a nested pure find_tables (strategy=_UNION_STRATEGY, use_layout=False)
    and, for each detected table, keeps its finder bbox and its row-major cell
    grid (Table.rows -- None for a gap). Candidates are deduped by rounded bbox
    (first kept), reproducing the engine's PythonTableFinderProvider plus
    _find_tables_union_candidates. Returns ``(candidates, finder)``; the finder is
    reused as the returned TableFinder shell (its textpage covers the whole page).
    """
    # Imported here, not at module top, to break the import cycle: this
    # module is itself imported lazily by table.find_tables (union path).
    from pymupdf.table import find_tables
    finder = find_tables(page, strategy=_UNION_STRATEGY, use_layout=False)
    candidates = []
    seen = set()
    for tab in (getattr(finder, "tables", None) or []):
        try:
            bbox = pymupdf.Rect(tab.bbox)
        except (ValueError, TypeError):
            continue
        if bbox.is_empty:
            continue
        grid = [[cell for cell in row.cells] for row in (tab.rows or [])]
        if not grid:
            continue
        key = tuple(round(value) for value in bbox)
        if key in seen:
            continue
        seen.add(key)
        candidates.append((bbox, grid))
    return candidates, finder


# --------------------------------------------------------------------------- #
# EXPERIMENTAL: MuPDF's TableHunter as the union candidate source.
#
# Selected with the environment variable PYMUPDF_TABLE_UNION_SOURCE=hunter
# (default: unset -> the line-based finder path below, byte-identical to the
# review branch). Exists so that upstream can drop a modified MuPDF/hunter
# build into the exact same fusion pipeline and read the effect directly off
# the ParseBench GTRM score. Measured on the unmodified 1.28.0 detector this
# path scores 0.5205 vs 0.7211 for the line finder (503 pages; matches the
# original engine-level investigation's 0.5206) -- the gap is grid
# over-segmentation, not region recovery. See the standalone study at
# https://github.com/veget-able/tablehunter-comparison for details.
# --------------------------------------------------------------------------- #

_HUNTER_PAD = 3.0  # points of slack around each layout table box


def _hunter_parse_bbox(text):
    if not text:
        return None
    try:
        parts = tuple(float(value) for value in text.split())
    except ValueError:
        return None
    return parts if len(parts) == 4 else None


def _hunter_table_cells(table_el):
    """Walk a std="Table" struct element into rows of TD bboxes.

    TR/TD nesting is taken from direct children only (a nested table's cells
    are not hoisted). Rows may be ragged where the detector emits a spanned
    cell as one wide/tall TD; empty rows are dropped.
    """
    rows = []
    for tr_el in table_el:
        if tr_el.tag != "struct" or tr_el.get("std") != "TR":
            continue
        row = []
        for td_el in tr_el:
            if td_el.tag != "struct" or td_el.get("std") != "TD":
                continue
            bbox = _hunter_parse_bbox(td_el.get("bbox"))
            if bbox is not None:
                row.append(bbox)
        if row:
            rows.append(row)
    return rows


def _hunter_layout_table_boxes(page):
    """All "table"-class layout boxes as non-empty Rects.

    Handles both shapes page.layout_information can carry: the raw dict form
    (get_layout(return_raw=True) -- group_bbox + class_name) and the
    normalized tuple form (x0, y0, x1, y1, class_name)."""
    boxes = []
    for box in page.layout_information or []:
        if isinstance(box, dict):
            if box.get("class_name") != "table":
                continue
            group_bbox = box.get("group_bbox")
            if not group_bbox:
                continue
            rect = pymupdf.Rect(group_bbox)
        elif len(box) >= 5 and box[4] == "table":
            rect = pymupdf.Rect(box[:4])
        else:
            continue
        if not rect.is_empty:
            boxes.append(rect)
    return boxes


def _union_hunter_candidates(page):
    """Hunter-driven union candidates: fz_find_table_within_bounds per box.

    Experimental counterpart of _union_line_candidates. It populates CHARS
    exactly like the nested line finder would (the downstream refine/span/
    header stages and Table.extract() read it) but performs no line-based
    detection -- the grid candidates come from MuPDF's bounded table detector
    instead. One detector textpage (TABLE_DETECTOR_FLAGS) is built per page
    and reused across boxes: the C function rewrites the stext block list in
    place and accumulates one Table struct per call, and the SWIG block
    wrapper does not expose the struct union, so the serialized XML is the
    supported walk. Returns (candidates, finder-shell) like its counterpart.
    """
    if not (hasattr(pymupdf, "mupdf") and hasattr(pymupdf.mupdf, "fz_find_table_within_bounds")):
        raise RuntimeError(
            "PYMUPDF_TABLE_UNION_SOURCE=hunter requires a PyMuPDF build that "
            "exposes pymupdf.mupdf.fz_find_table_within_bounds"
        )
    import xml.etree.ElementTree as ET

    from pymupdf.table import TABLE_DETECTOR_FLAGS, make_chars

    EDGES.clear()
    CHARS.clear()
    textpage = make_chars(page)
    shell = TableFinder(page)  # EDGES is empty: an empty shell, no line detection
    shell.textpage = textpage

    candidates = []
    boxes = _hunter_layout_table_boxes(page)
    if boxes:
        page_rect = pymupdf.Rect(page.rect)
        detector_tp = page.get_textpage(flags=TABLE_DETECTOR_FLAGS)
        stext = detector_tp.this
        for box in boxes:
            bounds = pymupdf.Rect(
                max(float(page_rect.x0), float(box.x0) - _HUNTER_PAD),
                max(float(page_rect.y0), float(box.y0) - _HUNTER_PAD),
                min(float(page_rect.x1), float(box.x1) + _HUNTER_PAD),
                min(float(page_rect.y1), float(box.y1) + _HUNTER_PAD),
            )
            if bounds.is_empty:
                continue
            pymupdf.mupdf.fz_find_table_within_bounds(
                stext,
                pymupdf.mupdf.FzRect(bounds.x0, bounds.y0, bounds.x1, bounds.y1),
            )
        seen = set()
        root = ET.fromstring(detector_tp.extractXML())
        for table_el in root.iter("struct"):
            if table_el.get("std") != "Table":
                continue
            bbox = _hunter_parse_bbox(table_el.get("bbox"))
            if bbox is None:
                continue
            rect = pymupdf.Rect(bbox)
            if rect.is_empty:
                continue
            grid = _hunter_table_cells(table_el)
            if not grid:
                continue
            key = tuple(round(value) for value in rect)
            if key in seen:
                continue
            seen.add(key)
            candidates.append((rect, grid))
    return candidates, shell


def _union_rect_area(rect):
    return max(0.0, float(rect.x1 - rect.x0)) * max(0.0, float(rect.y1 - rect.y0))


def _union_intersection_area(left, right):
    x0 = max(float(left.x0), float(right.x0))
    y0 = max(float(left.y0), float(right.y0))
    x1 = min(float(left.x1), float(right.x1))
    y1 = min(float(left.y1), float(right.y1))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _union_x_overlap(left, right):
    return max(0.0, min(float(left.x1), float(right.x1)) - max(float(left.x0), float(right.x0)))


def _union_find_owner(candidate_bbox, existing_bboxes):
    """The primary a split candidate belongs inside, plus an ambiguity flag.

    Returns ``(owner_index, ambiguous)``: owner is the best-contained primary
    (candidate>=_UNION_OWNER_CONTAINMENT inside it), else None; ambiguous is True
    when the candidate overlaps some primary enough to be unsafe to append."""
    candidate_area = _union_rect_area(candidate_bbox)
    if candidate_area <= 0:
        return None, True
    best_owner = None
    best_containment = 0.0
    ambiguous = False
    for index, existing_bbox in enumerate(existing_bboxes):
        existing_area = _union_rect_area(existing_bbox)
        inter_area = _union_intersection_area(candidate_bbox, existing_bbox)
        if inter_area <= 0 or existing_area <= 0:
            continue
        candidate_containment = inter_area / candidate_area
        existing_coverage = inter_area / existing_area
        if candidate_containment >= _UNION_OWNER_CONTAINMENT and candidate_containment > best_containment:
            best_owner = index
            best_containment = candidate_containment
        elif candidate_containment >= _UNION_OWNER_AMBIGUOUS_OVERLAP or existing_coverage >= _UNION_OWNER_AMBIGUOUS_OVERLAP:
            ambiguous = True
    return best_owner, ambiguous


def _union_text_span_rects(page):
    """Non-empty page text-span rects, cached on the page.

    Drives the grid-ref span-multiplicity gate. Distinct from _span_text_spans
    (which keeps only length>=2 spans as (rect, text) pairs): the gate wants every
    non-blank span as a bare rect, matching the engine's _page_text_span_rects."""
    cached = getattr(page, "_union_text_spans_cache", None)
    if cached is not None:
        return cached
    spans = []
    for block in page.get_text("dict").get("blocks", []) or []:
        for line in block.get("lines", []) or []:
            for span in line.get("spans", []) or []:
                if not str(span.get("text") or "").strip():
                    continue
                bbox = span.get("bbox")
                if not bbox:
                    continue
                rect = pymupdf.Rect(bbox)
                if not rect.is_empty:
                    spans.append(rect)
    try:
        setattr(page, "_union_text_spans_cache", spans)
    except Exception:
        pass
    return spans


def _union_cell_span_group_count(cell, text_spans):
    """Max horizontally-separated text-span groups on any single text line in a cell."""
    line_bands = []
    for span in text_spans:
        center_y = (float(span.y0) + float(span.y1)) / 2.0
        if center_y < float(cell.y0) - 1.0 or center_y > float(cell.y1) + 1.0:
            continue
        if _union_x_overlap(span, cell) <= 1.0:
            continue
        x0 = max(float(cell.x0), float(span.x0))
        x1 = min(float(cell.x1), float(span.x1))
        if x1 <= x0:
            continue
        for index, (band_y, intervals) in enumerate(line_bands):
            if abs(center_y - band_y) <= 4.0:
                intervals.append((x0, x1))
                line_bands[index] = ((band_y + center_y) / 2.0, intervals)
                break
        else:
            line_bands.append((center_y, [(x0, x1)]))
    best = 0
    for _, intervals in line_bands:
        groups = 0
        last_x1 = None
        for x0, x1 in sorted(intervals):
            if last_x1 is None or x0 - last_x1 > 4.0:
                groups += 1
                last_x1 = x1
            else:
                last_x1 = max(last_x1, x1)
        best = max(best, groups)
    return best


def _union_span_multiplicity(page, grid):
    """Max cell span-group count over a grid (high => the grid is under-segmented).

    Max, not average: under-segmentation often hits only a few cells (a merged
    header row, a sparse body), which an average would dilute below threshold."""
    if page is None:
        return None
    text_spans = _union_text_span_rects(page)
    best = None
    for row in grid:
        for cell in row:
            if cell is None:
                continue
            rect = pymupdf.Rect(cell)
            if rect.is_empty:
                continue
            count = _union_cell_span_group_count(rect, text_spans)
            if count > 0:
                best = count if best is None else max(best, count)
    return float(best) if best is not None else None


def _union_one_to_one_grid_refs(existing, candidates, *, iou_threshold, page, span_mult_gate, span_mult_threshold):
    """Primaries a candidate can grid-ref (replace grid with), 1:1 by IoU.

    ``existing``/``candidates`` are ``(bbox, grid)`` lists. Returns ``(refs,
    consumed)`` where ``refs`` maps a primary index to the candidate that should
    supply its grid (only mutual 1:1 IoU>=threshold matches that pass the
    span-multiplicity gate), and ``consumed`` is the set of candidate indexes
    thereby used up."""
    existing_matches = {}
    candidate_matches = {}
    for existing_index, (existing_bbox, _grid) in enumerate(existing):
        for candidate_index, (candidate_bbox, _cgrid) in enumerate(candidates):
            iou = _iou(existing_bbox, candidate_bbox)
            if iou >= iou_threshold:
                existing_matches.setdefault(existing_index, []).append((candidate_index, float(iou)))
                candidate_matches.setdefault(candidate_index, []).append((existing_index, float(iou)))
    refs = {}
    consumed = set()
    for existing_index, matches in existing_matches.items():
        if len(matches) != 1:
            continue
        candidate_index, _ = matches[0]
        if len(candidate_matches.get(candidate_index, [])) != 1:
            continue
        if span_mult_gate:
            span_mult = _union_span_multiplicity(page, candidates[candidate_index][1])
            if span_mult is not None and span_mult >= span_mult_threshold:
                continue
        refs[existing_index] = candidates[candidate_index]
        consumed.add(candidate_index)
    return refs, consumed


def _union_replace_append(existing, candidates, *, page, grid_ref, grid_ref_iou, span_mult_gate, span_mult_threshold):
    """Fuse primary and candidate ``(bbox, grid)`` entries.

    Applies grid-ref replacement, split replacement (>=2 candidates owned by one
    primary replace it, ordered by y0/x0) and append of unowned candidates,
    returning the fused entry list in the contractual order."""
    existing_bboxes = [entry[0] for entry in existing]
    if grid_ref:
        grid_refs, consumed = _union_one_to_one_grid_refs(
            existing,
            candidates,
            iou_threshold=grid_ref_iou,
            page=page,
            span_mult_gate=span_mult_gate,
            span_mult_threshold=span_mult_threshold,
        )
    else:
        grid_refs, consumed = {}, set()
    replacements = {}
    append_candidates = []
    for candidate_index, candidate in enumerate(candidates):
        if candidate_index in consumed:
            continue
        owner_index, ambiguous = _union_find_owner(candidate[0], existing_bboxes)
        if owner_index is not None:
            replacements.setdefault(owner_index, []).append(candidate)
        elif ambiguous:
            continue  # overlaps a primary but is not contained -> suppress
        else:
            append_candidates.append(candidate)
    final_replacements = {
        index: sorted(items, key=lambda entry: (float(entry[0].y0), float(entry[0].x0)))
        for index, items in replacements.items()
        if len(items) >= 2
    }
    entries = []
    for index, entry in enumerate(existing):
        if index in final_replacements:
            entries.extend(final_replacements[index])
        elif index in grid_refs:
            # Grid-ref: keep the primary's (layout) bbox, take the candidate grid.
            entries.append((entry[0], grid_refs[index][1]))
        else:
            entries.append(entry)
    entries.extend(append_candidates)
    return entries


def _find_tables_union(page):
    """Detect a page's tables by fusing layout grids with line-based candidates.

    (a) ensures the raw layout is present (computing it only when
    page.layout_information is None -- unlocked and with the analyzer's own
    default edge_threshold, matching the official use_layout path; the pymupdf4llm
    engine pre-populates it under its own lock, and a caller wanting a custom
    threshold can likewise pre-populate via page.get_layout), (b) reads the
    primary grids, (c) detects line candidates, (d) applies grid-ref / split /
    append, then returns a TableFinder whose .tables carry the fused grids in the
    contractual order. Each table's reported bbox is set explicitly (so a grid-ref
    table keeps its layout box); the grid is recoverable from Table.rows."""
    if page.layout_information is None:
        page.get_layout(return_raw=True)
    primaries = _layout_table_grids(page)
    # Experimental evaluation knob (see the hunter block above): route the
    # union's candidate source through MuPDF's TableHunter instead of the
    # Python line finder. Unset -> unchanged default path.
    if os.environ.get("PYMUPDF_TABLE_UNION_SOURCE", "").strip().lower() == "hunter":
        candidates, finder = _union_hunter_candidates(page)
    else:
        candidates, finder = _union_line_candidates(page)
    entries = _union_replace_append(
        primaries,
        candidates,
        page=page,
        grid_ref=True,
        grid_ref_iou=_UNION_GRID_REF_IOU,
        span_mult_gate=_UNION_GRID_REF_SPAN_MULT_GATE,
        span_mult_threshold=_UNION_GRID_REF_SPAN_MULT_THRESHOLD,
    )
    if finder is None:
        # Candidate detection failed mid-way; the nested find_tables may have
        # left partially-filled EDGES/CHARS state behind, and TableFinder's
        # constructor runs a full detection from that state -- clear it first
        # so the fallback really is an empty shell.
        EDGES.clear()
        CHARS.clear()
        finder = TableFinder(page)
    tables = []
    for bbox, grid in entries:
        flat = [cell for row in grid for cell in row if cell is not None]
        if not flat:
            continue
        tables.append(Table(page, flat, bbox=bbox))
    finder.tables = tables
    return finder
