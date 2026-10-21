"""Recover control-code glyphs from the actual embedded font's Unicode cmap.

No character is guessed from a font name or document name. MuPDF's glyph-name
fallback can turn e.g. an Adobe 'a19' glyph into control code 19 even though the
embedded font's cmap identifies that glyph as U+2713. Read that original cmap.
"""
import pymupdf


def _is_control(value):
    return len(value)==1 and ord(value)<32 and not value.isspace()


def _font_map(document, xref):
    cache = getattr(document, '_table_font_symbol_maps', None)
    if cache is None:
        cache = document._table_font_symbol_maps = {}
    if xref in cache:
        return cache[xref]
    mapping = {}
    payload = document.extract_font(xref)[3]
    if payload:
        font = pymupdf.Font(fontbuffer=payload)
        for codepoint in font.valid_codepoints():
            if codepoint < 32 or codepoint == 0xfffd:
                continue
            glyph = font.has_glyph(codepoint)
            name = pymupdf.mupdf.fz_get_glyph_name2(font.this, glyph)
            fallback = pymupdf.mupdf.fz_unicode_from_glyph_name(name)
            if 0 < fallback < 32 and _is_control(chr(fallback)):
                mapping.setdefault(chr(fallback), set()).add(chr(codepoint))
    result = {k:next(iter(v)) for k,v in mapping.items() if len(v)==1}
    cache[xref] = result
    return result


def control_glyphs(page, chars):
    indices = [i for i,ch in enumerate(chars) if ch['upright'] and _is_control(ch['text'])]
    if not indices:
        return ()
    # Font metadata is needed only for corrupt codes. This does not extract
    # page text again and never reopens the PDF or invokes OCR.
    fonts = page.get_fonts(full=True)
    records = []
    for i in indices:
        ch = chars[i]
        candidates = [f for f in fonts if f[3].split('+')[-1] == ch['fontname'].split('+')[-1]]
        values = {(_font_map(page.parent,f[0]).get(ch['text'])) for f in candidates}
        if len(values)!=1 or None in values:
            continue
        records.append(dict(char_index=i,original_text=ch['text'],text=values.pop(),
                            font_xrefs=tuple(sorted({f[0] for f in candidates})),
                            bbox=(ch['x0'],ch['top'],ch['x1'],ch['bottom'])))
    return tuple(records)
