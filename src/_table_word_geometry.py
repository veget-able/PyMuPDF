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



def notify_word_character_material(page, raw, epoch):
    """Register an existing producer delivery; never extract or match here."""
    epochs=getattr(page,'_table_word_character_epochs',None)
    if epochs is None:
        epochs={};page._table_word_character_epochs=epochs
    epochs[id(raw)]=(raw,epoch)
    # A notification denotes a new delivery, including a fresh runtime whose
    # local counter happens to equal the previous runtime's counter.
    material=getattr(page,'_table_word_character_material',None)
    if material is not None:
        material[1].pop(id(raw),None)
    geometry=getattr(page,'_table_word_geometry',None)
    if geometry is not None and geometry[1] is raw:
        page._table_word_geometry=None


def _word_character_epoch(page, raw):
    item=getattr(page,'_table_word_character_epochs',{}).get(id(raw))
    return item[1] if item is not None and item[0] is raw else None


def word_character_material(page, words, raw=None, *, epoch=None):
    """Share original native matches by real word/raw collection and epoch."""
    if raw is None:raw=getattr(page,'_table_raw_blocks',None)
    if raw is None:return (),{}
    if epoch is not None and epoch!=_word_character_epoch(page,raw):
        notify_word_character_material(page,raw,epoch)
    epoch=_word_character_epoch(page,raw)
    previous=getattr(page,'_table_word_character_material',None)
    if previous is None or previous[0] is not words:
        previous=(words,{})
        page._table_word_character_material=previous
    cached=previous[1].get(id(raw))
    if cached is None or cached[0] is not raw or cached[1]!=epoch:
        chars,matches=match_word_characters(raw,words)
        cached=(raw,epoch,chars,matches);previous[1][id(raw)]=cached
    return cached[2],cached[3]


def page_word_geometry(page, words):
    raw=getattr(page,'_table_raw_blocks',None)
    if raw is None:return {}
    epoch=_word_character_epoch(page,raw)
    cached=getattr(page,'_table_word_geometry',None)
    if (cached is not None and len(cached)==4 and cached[0] is words
            and cached[1] is raw and cached[3]==epoch):
        return cached[2]
    chars,matches=word_character_material(page,words,raw)
    geometry={wi:tuple(chars[i][3] for i in hits) for wi,hits in matches.items()}
    page._table_word_geometry=(words,raw,geometry,epoch)
    return geometry


def glyph_cell_owners(boxes, cells):
    """Whole glyphs must fit a unique actual cell; crossing/empty is unproved."""
    if not boxes:
        return []
    return [i for i,c in enumerate(cells) if c is not None
            and all(c[0] <= b[0] and c[1] <= b[1] and c[2] >= b[2] and c[3] >= b[3] for b in boxes)]
