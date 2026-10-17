"""Positive structural proofs for NEW ruling-table regions only.

Uses live finder glyphs and pre-snap source edges. Does not extract PDF content,
consult Layout class/GT, recognize headers, or change grid_ref/split permission.
Absence of a proof is not a non-table label: the original page content remains.
"""
from collections import Counter
from dataclasses import dataclass
import math
from statistics import median


@dataclass(frozen=True)
class Decision:
    rule: str | None
    reason: str
    evidence: dict

    @property
    def approved(self):
        return self.rule is not None


def _coverage(intervals, start, end):
    if end <= start:
        return 0.
    total, cursor = 0., start
    for a, b in sorted(intervals):
        a, b = max(a, start), min(b, end)
        if b > max(a, cursor):
            total += b - max(a, cursor)
        cursor = max(cursor, b)
    return total / (end - start)


def _record_support(cells, members, borders, glyphs, *, axis):
    """Same field/record contract along either physical page axis.

    A table need not fill every header slot or have its reading axis along x.
    Use already assigned concrete cells; never fabricate cells for None slots.
    """
    cross = 1-axis
    rows = {}
    for cell, ids, sides in zip(cells, members, borders):
        if ids:
            rows.setdefault((cell[cross], cell[cross+2]), []).append((cell, ids, sides))
    independent = []
    for row in rows.values():
        if len(row) < 2:
            continue
        ordered = sorted(row, key=lambda v: v[0][axis])
        gaps = []
        for (_, left, _), (_, right, _) in zip(ordered, ordered[1:]):
            height = median(glyphs[i][cross+2]-glyphs[i][cross] for i in left+right)
            gap = min(glyphs[i][axis] for i in right)-max(glyphs[i][axis+2] for i in left)
            gaps.append(gap >= .15*height)
        if all(gaps):
            independent.append(row)
    recurring = Counter((cell[axis], cell[axis+2])
                        for row in independent for cell,_,_ in row)
    repeated = sum(sum(recurring[(cell[axis],cell[axis+2])] >= 2
                       for cell,_,_ in row) >= 2 for row in independent)
    side_indices = (2, 3) if axis == 0 else (0, 1)
    ruled = sum(all(min(sides[i] for i in side_indices) >= .8 for _,_,sides in row)
                 for row in independent)
    return rows, independent, repeated, ruled


def _entry_schema(box, cells, members, glyphs, *, axis):
    """A complete repeated label/entry partition, not one accidental blank.

    Recovery only: small checkboxes and isolated one-row forms are not proven
    by this contract. Existing admission of those tables is unaffected.
    No label language, numeric vocabulary or benchmark identifier is used.
    """
    cross = 1-axis
    rows = {}
    for cell, ids in zip(cells, members):
        rows.setdefault((cell[cross], cell[cross+2]), []).append((cell, ids))
    if len(rows) < 2:
        return 0
    # Cell coordinates already share the finder's snapped boundaries. This
    # epsilon is for float arithmetic, not an extra snap/gap threshold.
    eps = 1e-6
    previous = box[cross]
    schema = None
    for (start, end), row in sorted(rows.items()):
        if abs(start-previous) > eps:
            return 0
        previous = end
        ordered = sorted(row, key=lambda pair: pair[0][axis])
        occupied = [bool(ids) for _, ids in ordered]
        if not any(occupied) or all(occupied):
            return 0
        boundary = box[axis]
        for cell, _ in ordered:
            if abs(cell[axis]-boundary) > eps:
                return 0
            boundary = cell[axis+2]
        if abs(boundary-box[axis+2]) > eps:
            return 0
        current = tuple((c[axis], c[axis+2], bool(ids)) for c,ids in ordered)
        if schema is not None and current != schema:
            return 0
        schema = current
        # A blank entry must have writing room, not be a narrow border strip.
        # Require a square of the row height and two local character heights.
        ids = [i for _, indices in ordered for i in indices]
        em = median(glyphs[i][cross+2]-glyphs[i][cross] for i in ids)
        if any(c[axis+2]-c[axis] < max(end-start, 2*em)
               for c, indices in ordered if not indices):
            return 0
    return len(rows) if abs(previous-box[cross+2]) <= eps else 0


class PageEvidence:
    """One immutable finder-call snapshot; no global/page-number cache."""

    def __init__(self, chars, edges, *, snap_x=3., snap_y=3., cell_glyphs=None):
        self.cell_glyphs = cell_glyphs
        self.raw_to_valid = {}
        self.descriptions = {}
        glyphs = []
        for raw_id, char in enumerate(chars):
            text = str(char.get('text') or '')
            if not text.strip():
                continue
            try:
                x0, x1 = float(char['x0']), float(char['x1'])
                y0, y1 = float(char['top']), float(char['bottom'])
            except (TypeError, ValueError, KeyError):
                continue
            if not all(math.isfinite(v) for v in (x0, x1, y0, y1)) or y1 <= y0:
                continue
            self.raw_to_valid[raw_id] = len(glyphs)
            glyphs.append((x0, y0, x1, y1, text))
        self.glyphs = glyphs
        self.snap_x, self.snap_y = snap_x, snap_y
        self.horizontal, self.vertical = [], []
        for edge in edges:
            if edge.get('ruling_origin') not in ('vector', 'raster'):
                continue
            if edge.get('orientation') == 'h':
                self.horizontal.append((float(edge['top']), float(edge['x0']), float(edge['x1'])))
            elif edge.get('orientation') == 'v':
                self.vertical.append((float(edge['x0']), float(edge['top']), float(edge['bottom'])))
        try:
            import numpy as np
        except ImportError:
            self.centers = None
        else:
            self.centers = np.asarray([((a+c)/2, (b+d)/2) for a,b,c,d,_ in glyphs], dtype='float64').reshape(-1, 2)

    def members(self, box):
        if self.cell_glyphs is not None:
            return [self.raw_to_valid[i] for i in self.cell_glyphs.members(box)
                    if i in self.raw_to_valid]
        x0, y0, x1, y1 = box
        if self.centers is not None:
            x, y = self.centers.T
            return ((x >= x0) & (x < x1) & (y >= y0) & (y < y1)).nonzero()[0].tolist()
        return [i for i,(a,b,c,d,_) in enumerate(self.glyphs)
                if x0 <= (a+c)/2 < x1 and y0 <= (b+d)/2 < y1]

    def borders(self, box):
        x0, y0, x1, y1 = box
        return (
            _coverage([(a,b) for x,a,b in self.vertical if abs(x-x0) <= self.snap_x], y0,y1),
            _coverage([(a,b) for x,a,b in self.vertical if abs(x-x1) <= self.snap_x], y0,y1),
            _coverage([(a,b) for y,a,b in self.horizontal if abs(y-y0) <= self.snap_y], x0,x1),
            _coverage([(a,b) for y,a,b in self.horizontal if abs(y-y1) <= self.snap_y], x0,x1))

    def describe(self, box, grid):
        key = (tuple(box), tuple(tuple(None if c is None else tuple(c) for c in row) for row in grid))
        if key not in self.descriptions:
            self.descriptions[key] = self._describe(box, grid)
        return dict(self.descriptions[key])

    def _describe(self, box, grid):
        cells = list(dict.fromkeys(tuple(map(float, c)) for row in grid for c in row
                                  if c is not None and c[2] > c[0] and c[3] > c[1]))
        members = [self.members(c) for c in cells]
        borders = [self.borders(c) for c in cells]
        # A glyph assigned to multiple overlapping concrete cells is not an
        # independent field. None slots are not cells and were removed above.
        owners = Counter(i for ids in members for i in ids)
        cut = set()
        for cell, ids in zip(cells, members):
            x0,y0,x1,y1 = cell
            for i in ids:
                a,b,c,d,_ = self.glyphs[i]
                # Ignore tiny font-box overhang and exterior clipping. Only
                # internal boundaries can fabricate extra independent fields.
                xtol = min(1., .2*max(c-a, 0.))
                ytol = min(1., .2*(d-b))
                if any(box[0]+1e-6 < x < box[2]-1e-6 and a+xtol < x < c-xtol for x in (x0,x1)):
                    cut.add(i)
                if any(box[1]+1e-6 < y < box[3]-1e-6 and b+ytol < y < d-ytol for y in (y0,y1)):
                    cut.add(i)
        populated = sum(bool(ids) for ids in members)
        # Explicit cell intervals must recur in distinct rows. Rowspans alone
        # cannot manufacture a second record; each concrete cell occurs once.
        rows, independent, repeated_rows, horizontal_rows = _record_support(
            cells, members, borders, self.glyphs, axis=0)
        _, _, repeated_columns, vertical_columns = _record_support(
            cells, members, borders, self.glyphs, axis=1)
        # Sparse forms have actual empty compartments beside labels, not just
        # a blank slot introduced by row/colspan serialization.
        all_rows = {}
        for cell, ids, sides in zip(cells, members, borders):
            all_rows.setdefault((cell[1],cell[3]), []).append((cell, ids, sides))
        form_rows = sum(any(ids for _,ids,_ in row) and any(not ids for _,ids,_ in row)
                        and not any(i in cut for _,ids,_ in row for i in ids)
                        and all(min(sides) >= .8 for _,_,sides in row)
                        for row in all_rows.values())
        entry_rows = max(_entry_schema(box, cells, members, self.glyphs, axis=axis)
                         for axis in (0, 1)) if form_rows and not cut else 0
        spanning = any(sum(a >= cell[0] and c <= cell[2] for (a,b,c,d),_,_ in row) >= 2
                       for cell, ids in zip(cells, members) if ids
                       for row in independent if row[0][0][1] >= cell[3])
        area = max(0.,box[2]-box[0])*max(0.,box[3]-box[1])
        tile_ratio = sum((c[2]-c[0])*(c[3]-c[1]) for c in cells)/area if area else 0.
        return dict(cells=len(cells), populated=populated, glyphs=len(owners),
                    duplicated=sum(n>1 for n in owners.values()), cut=len(cut),
                    bordered=sum(min(s) >= .8 for s in borders),
                    tile_ratio=tile_ratio, repeated_rows=repeated_rows,
                    horizontal_rows=horizontal_rows, row_count=len(rows),
                    repeated_columns=repeated_columns, vertical_columns=vertical_columns,
                    col_count=len({(c[0],c[2]) for c in cells}),
                    independent_rows=len(independent), form_rows=form_rows,
                    entry_schema_rows=entry_rows,
                    spanning=spanning)


def decide_append(box, grid, materials, *, external_owner=None):
    if materials is None:
        return Decision(None, 'missing_material', {})
    e = materials.describe(box, grid)
    if e['cells'] < 2 or not e['populated']:
        return Decision(None, 'no_multiple_fields', e)
    if external_owner:
        return Decision(None, 'belongs_to_non_table_component', dict(e, external_owner=external_owner))
    if e['duplicated']:
        return Decision(None, 'nonindependent_text_fields', e)
    if e['tile_ratio'] > 1.01:
        return Decision(None, 'overlapping_partition', e)
    # Explicit field compartments support sparse forms and one-dimensional
    # tables without inventing a density requirement for blank entry fields.
    if e['bordered'] == e['cells']:
        if e['repeated_rows'] >= 2 or (e['repeated_columns'] >= 2 and not e['cut']):
            return Decision('ruled_records', 'source_supported_repeated_fields', e)
        if e['form_rows'] >= 1:
            return Decision('ruled_form', 'labels_and_empty_compartments', e)
        if e['spanning'] and e['independent_rows'] >= 1 and not e['cut']:
            return Decision('spanning_record', 'parent_compartment_and_separated_fields', e)
        if e['row_count'] == 1 and e['independent_rows'] == 1:
            return Decision('single_record', 'separated_fields_in_one_ruled_row', e)
        if e['col_count'] == 1 and e['row_count'] >= 2 and not e['cut']:
            return Decision('single_column', 'separated_compartments_in_one_column', e)
    # Partial-ruling records need BOTH recurring concrete field intervals and
    # horizontal separators, not merely text inside arbitrary rectangles.
    if ((e['repeated_rows'] >= 2 and e['horizontal_rows'] >= 2)
            or (e['repeated_columns'] >= 2 and e['vertical_columns'] >= 2 and not e['cut'])):
        return Decision('partially_ruled_records', 'repeated_fields_and_row_rules', e)
    return Decision(None, 'no_table_structure_proof', e)
