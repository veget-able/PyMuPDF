"""Approximate substring search, with offsets into the extracted page text."""

from itertools import groupby


def _normalize(text):
    """Case-fold and collapse whitespace, retaining original character ranges."""
    chars, offsets = [], []
    i = 0
    while i < len(text):
        # Join a word split across consecutive lines, but not across blocks
        # (which are separated by two newlines). Keep the original hyphen in
        # the returned text and geometry.
        if (text[i:i + 2] == "-\n" and i and text[i - 1].isalpha()
                and i + 2 < len(text) and text[i + 2].isalpha()):
            i += 2
            continue
        char = text[i]
        if char.isspace():
            if chars and chars[-1] == " ":
                offsets[-1] = (offsets[-1][0], i + 1)
            else:
                chars.append(" ")
                offsets.append((i, i + 1))
        else:
            folded = char.casefold()
            chars.extend(folded)
            offsets.extend([(i, i + 1)] * len(folded))
        i += 1
    return "".join(chars), offsets


def _windows(text, needle, max_edits):
    """A match with k edits must contain one of k+1 query pieces unchanged."""
    size = len(needle)
    windows = []
    for part in range(max_edits + 1):
        offset = part * size // (max_edits + 1)
        piece = needle[offset:(part + 1) * size // (max_edits + 1)]
        pos = text.find(piece)
        while pos >= 0:
            windows.append((max(0, pos - offset - max_edits),
                            min(len(text), pos - offset + size + max_edits)))
            # Repetitive text or large budgets can make filtering cost more
            # than a full scan. Bound the work and memory spent on seed hits.
            if len(windows) * size >= len(text):
                return [(0, len(text))]
            pos = text.find(piece, pos + 1)
    merged = []
    for start, end in sorted(windows):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _candidates(text, needle, max_edits, boundaries=None):
    """Yield (distance, start, end), choosing the earliest optimal start per end."""
    size = len(needle)
    if max_edits == 0:
        start = text.find(needle)
        while start >= 0:
            end = start + size
            if boundaries is None or (boundaries[start] and boundaries[end]):
                yield 0, start, end
            start = text.find(needle, start + 1)
        return

    for first, last in _windows(text, needle, max_edits):
        bounds = boundaries[first:last + 1] if boundaries is not None else None
        for cost, start, end in _levenshtein(text[first:last], needle, max_edits, bounds):
            yield cost, first + start, first + end


def _levenshtein(text, needle, max_edits, boundaries):
    """Semi-global Levenshtein, with two rows of costs and start offsets.

    Skipping a text prefix is free; deleting a query character costs one.
    """
    size = len(needle)
    previous = list(range(size + 1))
    if boundaries is not None and not boundaries[0]:
        previous = [size + 1] * (size + 1)
    starts = [0] * (size + 1)
    for end, char in enumerate(text, 1):
        current = [0] * (size + 1)
        boundary = boundaries is None or boundaries[end]
        if not boundary:
            current[0] = size + 1  # Do not start inside a case-folded glyph.
        current_starts = [end] * (size + 1)
        for i, wanted in enumerate(needle, 1):
            cost = previous[i - 1] + (char != wanted)
            start = starts[i - 1]
            insertion = previous[i] + 1
            if insertion < cost or (insertion == cost and starts[i] < start):
                cost, start = insertion, starts[i]
            deletion = current[i - 1] + 1
            if deletion < cost or (deletion == cost and current_starts[i - 1] < start):
                cost, start = deletion, current_starts[i - 1]
            current[i], current_starts[i] = cost, start
        if boundary and current[-1] <= max_edits and current_starts[-1] < end:
            yield current[-1], current_starts[-1], end
        previous, starts = current, current_starts


def _page_text(raw):
    """Return text, per-character (span, char) references, and original spans."""
    text, refs, spans = [], [], []
    for block in raw["blocks"]:
        if block["type"] != 0:
            continue
        if text:
            text.append("\n")
            refs.append(None)
        for line in block["lines"]:
            for span in line["spans"]:
                span_index = len(spans)
                spans.append((line["dir"], span))
                for char_index, char in enumerate(span["chars"]):
                    text.extend(char["c"])
                    refs.extend([(span_index, char_index)] * len(char["c"]))
            text.append("\n")
            refs.append(None)
    return "".join(text), refs, spans


def search_for_fuzzy(page, needle, *, max_edits, clip=None, textpage=None):
    from . import CheckParent, TEXT_MEDIABOX_CLIP, TEXT_PRESERVE_LIGATURES
    from . import TEXT_PRESERVE_WHITESPACE, recover_span_quad

    CheckParent(page)
    if not isinstance(needle, str):
        raise TypeError("needle must be a string")
    if not isinstance(max_edits, int) or isinstance(max_edits, bool):
        raise TypeError("max_edits must be an integer")
    if max_edits < 0:
        raise ValueError("max_edits must be non-negative")
    needle = _normalize(needle)[0].strip()
    if not needle:
        return []
    if max_edits >= len(needle):
        raise ValueError("max_edits must be less than the normalized needle length")
    if textpage is None:
        # Preserve the actual line breaks, hyphens and glyphs for result text
        # and quads. Normalization happens only in the search representation.
        textpage = page.get_textpage(clip=clip, flags=(
            TEXT_PRESERVE_WHITESPACE | TEXT_PRESERVE_LIGATURES | TEXT_MEDIABOX_CLIP
        ))
    elif getattr(textpage, "parent", None) != page:
        raise ValueError("not a textpage of this page")

    original, refs, spans = _page_text(textpage.extractRAWDICT())
    text, offsets = _normalize(original)
    boundaries = [True] + [a[0] != b[0] for a, b in zip(offsets, offsets[1:])] + [True]
    candidates = sorted(_candidates(text, needle, max_edits, boundaries),
                        key=lambda hit: (hit[0], abs(hit[2] - hit[1] - len(needle)),
                                         hit[1], hit[2]))
    # Resolve overlaps in original coordinates too: case-folding can expand
    # one glyph (e.g. sharp s) into several searchable characters.
    occupied = bytearray(len(original))
    selected = []
    for distance, start, end in candidates:
        first, last = offsets[start][0], offsets[end - 1][1]
        if any(occupied[first:last]):
            continue
        occupied[first:last] = b"\1" * (last - first)
        selected.append((first, last, distance))

    results = []
    for first, last, distance in sorted(selected):
        quads = []
        for span_index, group in groupby(refs[first:last],
                                        key=lambda ref: ref[0] if ref else None):
            if span_index is None:
                continue
            chars = list(group)
            direction, span = spans[span_index]
            quads.append(recover_span_quad(direction, span,
                         span["chars"][chars[0][1]:chars[-1][1] + 1]))
        results.append(dict(text=original[first:last], distance=distance, quads=quads))
    return results
