"""Independent-region admission using existing finder text and graphic evidence.

This is not a cell-grid validity test: diagrams and equations can have valid
grids. A negative result only removes permission to create an unowned table.
No extraction, model call, benchmark label, or filename is used here.
"""
import re


def delimiter_envelopes(chars):
    # Unicode extensible parentheses and Adobe Symbol PUA equivalents.
    # PUA is accepted only in a mathematical extension / Symbol font.
    groups = {}
    for c in chars:
        text = c['text']
        side = None
        if text in ('(', '⎛', '⎜', '⎝'):
            side = 'left'
        elif text in (')', '⎞', '⎟', '⎠'):
            side = 'right'
        elif ('CMEX' in c.get('fontname', '').upper()
              or 'SYMBOL' in c.get('fontname', '').upper()):
            if text in ('\uf8eb', '\uf8ec', '\uf8ed'):
                side = 'left'
            elif text in ('\uf8f6', '\uf8f7', '\uf8f8'):
                side = 'right'
        if side:
            key = (side, round(c['x0'], 1), round(c['x1'], 1))
            groups.setdefault(key, []).append((c['top'], c['bottom']))
    envelopes = []
    for (side, x0, x1), spans in groups.items():
        top = bottom = None
        for a, b in sorted(spans):
            if top is None:
                top, bottom = a, b
            elif a <= bottom + 1:
                bottom = max(bottom, b)
            else:
                envelopes.append((side, (x0, top, x1, bottom)))
                top, bottom = a, b
        if top is not None:
            envelopes.append((side, (x0, top, x1, bottom)))
    return envelopes


def enclosed_by_math(bbox, envelopes):
    x0, y0, x1, y1 = bbox
    for side, left in envelopes:
        if side != 'left' or left[2] > x0 + 1 or left[1] > y0 + 1 or left[3] < y1 - 1:
            continue
        height = left[3] - left[1]
        if height < 2 * (y1 - y0):
            continue
        for other, right in envelopes:
            if (other == 'right' and right[0] >= x1 - 1
                    and abs(right[1] - left[1]) <= 1
                    and abs(right[3] - left[3]) <= 1
                    and right[0] - left[2] <= 2 * height):
                return True
    return False


def graphic_primitives(paths):
    """Read original paths, not snap/join or synthesized ruling edges."""
    triangles, diagonal = [], []
    for path in paths:
        items = path['items']
        if path.get('fill') is not None and len(items) == 3 and all(i[0] == 'l' for i in items):
            vertices = {tuple(p) for i in items for p in i[1:3]}
            if len(vertices) == 3:
                triangles.append(tuple(path['rect']))
        if 's' not in path['type']:
            continue
        for item in items:
            if item[0] != 'l':
                continue
            a, b = item[1:3]
            # Oblique strokes are curve/diagram material, not table rules.
            if abs(a[0] - b[0]) > .1 and abs(a[1] - b[1]) > .1:
                diagonal.append(((a[0]+b[0])/2, (a[1]+b[1])/2))
    return triangles, diagonal


class CellGlyphs:
    """Raw, ordered half-open membership shared within one finder call."""
    def __init__(self, chars):
        self.chars = list(chars)
        self.cache = {}
        try:
            import numpy as np
        except ImportError:
            self.centers = None
        else:
            self.centers = np.asarray([
                ((c['x0']+c['x1'])/2, (c['top']+c['bottom'])/2)
                for c in self.chars], dtype='float64').reshape(-1, 2)

    def members(self, cell):
        cell = tuple(cell)
        if cell not in self.cache:
            if self.centers is None:
                ids = [i for i,c in enumerate(self.chars)
                       if cell[0] <= (c['x0']+c['x1'])/2 < cell[2]
                       and cell[1] <= (c['top']+c['bottom'])/2 < cell[3]]
            else:
                x, y = self.centers.T
                ids = ((x >= cell[0]) & (x < cell[2]) &
                       (y >= cell[1]) & (y < cell[3])).nonzero()[0].tolist()
            self.cache[cell] = ids
        return self.cache[cell]


def grid_cell_texts(grid, chars, *, glyphs=None):
    cells = list(dict.fromkeys(tuple(c) for row in grid for c in row if c is not None))
    glyphs = glyphs if glyphs is not None else CellGlyphs(chars)
    texts = [''.join(glyphs.chars[i]['text'] for i in glyphs.members(c)).strip()
             for c in cells]
    return list(zip(cells, texts))


def append_veto(bbox, grid, chars, *, envelopes, triangles, diagonal, picture,
                cell_texts=None):
    if enclosed_by_math(bbox, envelopes):
        return 'enclosing_math_delimiters'
    if cell_texts is None:
        cell_texts = grid_cell_texts(grid, chars)
    cells = [c for c,t in cell_texts]
    occupied = [(c, t) for c, t in cell_texts if t]
    if graphical_panel_grid(occupied, diagonal):
        return 'graphical_panels_with_only_panel_labels'
    if external_callouts(bbox, grid, cells, occupied, triangles, picture):
        return 'symbol_array_with_external_callouts'
    return None


def graphical_panel_grid(occupied, diagonal):
    # A panel-label grid is not sufficient: require non-ruling graph strokes
    # distributed inside at least two labelled panels as independent evidence.
    if len(occupied) >= 2 and all(re.fullmatch(r'\([\w]\)', t) for _, t in occupied):
        graphical_cells = 0
        for c, _ in occupied:
            points = [(x, y) for x, y in diagonal if c[0]+1 < x < c[2]-1 and c[1]+1 < y < c[3]-1]
            if (len(points) >= 12
                    and max(x for x,y in points)-min(x for x,y in points) >= .5*(c[2]-c[0])
                    and max(y for x,y in points)-min(y for x,y in points) >= .25*(c[3]-c[1])):
                graphical_cells += 1
        if graphical_cells >= 2:
            return True
    return False


def external_callouts(bbox, grid, cells, occupied, triangles, picture):
    # Single-letter arrays remain valid tables unless separate graphical
    # callouts point to the array. No P/N text or fixed cell count requirement.
    if (picture and len(grid) == 1 and len(occupied) >= 2
            and len(occupied) == len(cells)
            and all(len(t) == 1 and t.isalpha() for _, t in occupied)):
        x0, y0, x1, y1 = bbox
        height = y1-y0
        tips = []
        for a,b,c,d in triangles:
            if not (a < x1 and c > x0):
                continue
            near_top = y0-.35*height <= d <= y0+.15*height and b < y0
            near_bottom = y1-.15*height <= b <= y1+.35*height and d > y1
            if near_top or near_bottom:
                tips.append((a+c)/2)
        if len(tips) >= 2 and max(tips)-min(tips) > .1*height:
            return True
    return False


class AppendContext:
    """Finder-call inputs retained before scope exit; verdicts only on demand.

    All admitted peers remain evidence even if grid_ref/split consumes them.
    No live page/proxy, global CHARS or drawing-cache lookup during selection.
    """
    def __init__(self, chars, edges, paths=(), image_boxes=()):
        self.chars = tuple(dict(c) for c in chars)
        self.edges = tuple(dict(e) for e in edges)
        self.paths = tuple(paths)  # read-only producer drawings, before conversion
        self.image_boxes = tuple(tuple(b) for b in image_boxes)
        self._glyphs = self._materials = self._graphics = self._envelopes = None
        self._components = None
        self.candidates = []
        self.support = []
        self._texts = {}
        self._verdicts = {}

    @property
    def glyphs(self):
        if self._glyphs is None:
            self._glyphs = CellGlyphs(self.chars)
        return self._glyphs

    @property
    def materials(self):
        if self._materials is None:
            from ._table_append_structure import PageEvidence
            self._materials = PageEvidence(self.chars, self.edges, cell_glyphs=self.glyphs)
        return self._materials

    def add(self, bbox, grid, picture, support):
        assert self._components is None and not self._verdicts
        index = len(self.candidates)
        frozen_grid = tuple(tuple(None if c is None else tuple(c) for c in row) for row in grid)
        self.candidates.append((tuple(bbox), frozen_grid, picture))
        self.support.append(support)
        return index

    def texts(self, index):
        if index not in self._texts:
            self._texts[index] = grid_cell_texts(self.candidates[index][1], self.chars,
                                                glyphs=self.glyphs)
        return self._texts[index]

    def veto(self, index):
        if index in self._verdicts:
            return self._verdicts[index]
        box, grid, picture = self.candidates[index]
        if self._envelopes is None:
            self._envelopes = delimiter_envelopes(self.chars)
        # No cell text or vector analysis for a proven enclosing formula.
        if enclosed_by_math(box, self._envelopes):
            reason = 'enclosing_math_delimiters'
        else:
            if self._graphics is None:
                self._graphics = graphic_primitives(self.paths)
            triangles, diagonal = self._graphics
            reason = append_veto(box, grid, self.chars, envelopes=(),
                                 triangles=triangles, diagonal=diagonal, picture=picture,
                                 cell_texts=self.texts(index))
            if reason is None:
                if self._components is None:
                    from ._table_component_context import component_vetoes
                    from ._table_union import _UnionGlyphIntervals, _union_grid_has_2d_content_support
                    missing = [i for i,s in enumerate(self.support) if s is None]
                    if missing:
                        glyphs = _UnionGlyphIntervals(self.chars)
                        for i in missing:
                            self.support[i] = _union_grid_has_2d_content_support(
                                self.candidates[i][1], glyphs=glyphs)
                    self._components = component_vetoes(
                        self.candidates, self.chars, self.paths, self.image_boxes,
                        cell_texts=[self.texts(i) for i in range(len(self.candidates))],
                        content_support=self.support, triangles=triangles)
                reason = self._components.get(index)
        self._verdicts[index] = reason
        return reason

    def decide(self, index):
        from ._table_append_structure import Decision, decide_append
        reason = self.veto(index)
        if reason:
            return Decision(None, 'belongs_to_non_table_component', {'external_owner': reason})
        box, grid, _ = self.candidates[index]
        return decide_append(box, grid, self.materials)
