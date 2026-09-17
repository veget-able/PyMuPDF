"""Word/glyph correspondence from already extracted RAWDICT and word cache."""
from collections import defaultdict
from pymupdf import Rect
from pymupdf._table_refine import _WordCenterIndex
from pymupdf._table_spans import _span_point_in_rect


def match_word_characters(raw_blocks, words):
    raw = [(s, l['dir'], (bi,li)) for bi,b in enumerate(raw_blocks) if b.get('type') == 0
           for li,l in enumerate(b['lines']) for s in l['spans']]
    chars, points = [], []
    for si, (rs, direction, source_line) in enumerate(raw):
        for ch in rs['chars']:
            if not ch['c'].strip():
                continue
            b = ch['bbox']; cx, cy = (b[0]+b[2])/2, (b[1]+b[3])/2
            # The glyph center and its baseline are already extracted data.
            # Vertical writing uses the baseline x; horizontal writing uses y.
            px, py = (cx, ch['origin'][1]) if abs(direction[0]) >= abs(direction[1]) else (ch['origin'][0], cy)
            chars.append((si, ch['c'], source_line, tuple(b)))
            points.extend([(cx,cy,cx,cy,ch['c']), (px,py,px,py,ch['c'])])
    index = _WordCenterIndex(points)
    matches, owners = {}, defaultdict(set)
    for wi, w in enumerate(words):
        rect = Rect(w[:4])
        hits = sorted({i//2 for i in index.candidates(rect)
                       if _span_point_in_rect(points[i][0], points[i][1], rect)})
        # Font-height boxes can overlap neighbouring text lines. Retain the
        # original RAWDICT line identities rather than concatenating neighbours.
        lines = defaultdict(list)
        for ci in hits: lines[chars[ci][2]].append(ci)
        candidates = [cs for cs in lines.values() if ''.join(chars[i][1] for i in cs) == w[4]]
        if len(candidates) == 1:
            matches[wi] = candidates[0]
            for ci in candidates[0]: owners[ci].add(wi)
    return chars, {wi: hits for wi,hits in matches.items()
                   if all(len(owners[ci]) == 1 for ci in hits)}


def page_word_geometry(page, words):
    raw = getattr(page, '_table_raw_blocks', None)
    if raw is None:
        return {}
    cached = getattr(page, '_table_word_geometry', None)
    if cached is not None and cached[0] is words and cached[1] is raw:
        return cached[2]
    chars, matches = match_word_characters(raw, words)
    geometry = {wi: tuple(chars[i][3] for i in hits) for wi,hits in matches.items()}
    page._table_word_geometry = (words, raw, geometry)
    return geometry


def glyph_cell_owners(boxes, cells):
    """Whole glyphs must fit a unique actual cell; crossing/empty is unproved."""
    if not boxes:
        return []
    return [i for i,c in enumerate(cells) if c is not None
            and all(c[0] <= b[0] and c[1] <= b[1] and c[2] >= b[2] and c[3] >= b[3] for b in boxes)]
