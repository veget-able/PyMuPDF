"""Call-local painted text/clip ownership for structured table consumers.

TextPage and ordinary drawings discard the active clipping stack. This device
collects that missing relation once from the already-open page. It does not
reopen a PDF, render pixels, run OCR, or interpret rulings a second time.
"""

import math

import pymupdf as pm
from pymupdf import mupdf


def area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1]) if b else 0.0


def intersect(a, b):
    if a is None or b is None:
        return None
    return [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]


class ClipDevice(pm.JM_new_lineart_device_Device):
    def __init__(self):
        super().__init__([], False, None)
        self.stack = []
        self.events = []
        self.glyphs = []
        self.unique = {}
        self.paints = []
        self.unsafe = 0
        self.groups = []
        self.error = None
        self.use_virtual_fill_text()
        self.use_virtual_stroke_text()
        self.use_virtual_ignore_text()
        self.use_virtual_begin_tile()
        self.use_virtual_end_tile()
        self.use_virtual_begin_mask()
        self.use_virtual_end_mask()
        if hasattr(self, "use_virtual_begin_metatext"):
            self.use_virtual_begin_metatext()
            self.use_virtual_end_metatext()

    def _rect(self, ctx, path, ctm):
        self.ctm = mupdf.FzMatrix(ctm)
        self.path_type = pm.trace_device_FILL_PATH
        pm.jm_lineart_path(self, ctx, path)
        items = (self.pathdict or {}).get("items", ())
        if len(items) == 1 and items[0][0] == "re":
            return list(pm.Rect(items[0][1]).normalize())
        return None

    def clip_path(self, ctx, path, even_odd, ctm, scissor):
        box = self._rect(ctx, path, ctm)
        if self.stack:
            box = intersect(box, self.events[self.stack[-1]]["bbox"])
        self.events.append(dict(bbox=box, glyph_ids=[], unknown_text=False, unknown_paint=bool(self.unsafe)))
        self.stack.append(len(self.events) - 1)

    def _unknown_clip(self, *args):
        self.events.append(dict(bbox=None, glyph_ids=[], unknown_text=True, unknown_paint=True))
        self.stack.append(len(self.events) - 1)

    clip_text = _unknown_clip
    clip_stroke_text = _unknown_clip
    clip_stroke_path = _unknown_clip
    clip_image_mask = _unknown_clip

    def pop_clip(self, ctx):
        if not self.stack:
            self.error = "Unbalanced table clip stack"
            raise ValueError("Unbalanced table clip stack")
        self.stack.pop()

    def begin_mask(self, ctx, *args):
        # Painting the soft mask is not page content. end_mask installs it as
        # an unsupported clipping scope, which a later pop_clip removes.
        self.unsafe += 1

    def end_mask(self, ctx, *args):
        self.unsafe -= 1
        self._unknown_clip()

    def begin_group(self, ctx, bbox, cs, isolated, knockout, blendmode, alpha):
        unsafe = bool(knockout or blendmode or alpha != 1)
        self.groups.append(unsafe)
        self.unsafe += unsafe

    def end_group(self, ctx):
        self.unsafe -= self.groups.pop()

    def begin_tile(self, ctx, *args):
        self.unsafe += 1
        return 0

    def end_tile(self, ctx):
        self.unsafe -= 1

    def begin_metatext(self, ctx, *args):
        self.unsafe += 1

    def end_metatext(self, ctx):
        self.unsafe -= 1

    def _text(self, text, ctm, alpha):
        if self.unsafe or alpha != 1 or any(self.events[i]["bbox"] is None for i in self.stack):
            for i in self.stack:
                self.events[i]["unknown_text"] = True
            return
        span = text.head
        while span:
            s = mupdf.FzTextSpan(span)
            matrix = mupdf.fz_concat(s.trm(), mupdf.FzMatrix(ctm))
            if s.m_internal.wmode or matrix.a <= 0 or abs(matrix.b) > max(0.001, abs(matrix.a) * 0.001):
                for i in self.stack:
                    self.events[i]["unknown_text"] = True
                span = span.next
                continue
            size = math.hypot(matrix.a, matrix.b)
            font = pm.JM_font_name(s.font())
            for j in range(s.m_internal.len):
                item = s.items(j)
                point = mupdf.fz_transform_point(mupdf.FzPoint(item.x, item.y), mupdf.FzMatrix(ctm))
                advance = mupdf.fz_advance_glyph(s.font(), item.gid, 0) * size if item.gid >= 0 else 0
                text_value = chr(item.ucs) if 0 <= item.ucs <= 0x10FFFF else "\ufffd"
                g = dict(x0=point.x, x1=point.x + advance, y=point.y, size=size, text=text_value, font=font)
                if self.stack:
                    b = self.events[self.stack[-1]]["bbox"]
                    if not (b[0] <= (g["x0"] + g["x1"]) / 2 <= b[2] and b[1] <= g["y"] <= b[3]):
                        continue
                key = tuple(round(g[k], 3) for k in ("x0", "x1", "y", "size")) + (text_value,)
                if key not in self.unique:
                    self.unique[key] = len(self.glyphs)
                    self.glyphs.append(g)
                index = self.unique[key]
                for i in self.stack:
                    self.events[i]["glyph_ids"].append(index)
            span = span.next

    def fill_text(self, ctx, text, ctm, cs, color, alpha, cp):
        self._text(text, ctm, alpha)

    def stroke_text(self, ctx, text, stroke, ctm, cs, color, alpha, cp):
        self._text(text, ctm, alpha)

    def ignore_text(self, *args):
        pass

    def fill_path(self, ctx, path, even_odd, ctm, cs, color, alpha, cp):
        b = self._rect(ctx, path, ctm)
        if b is None:
            # An unsupported paint cannot establish a uniform background.
            b = list(pm.JM_py_from_rect(self.pathrect))
            known = False
        else:
            known = alpha == 1 and not self.unsafe
        if self.stack:
            clip = self.events[self.stack[-1]]["bbox"]
            if clip is None:
                known = False
            else:
                b = intersect(b, clip)
        rgb = pm.jm_lineart_color(cs, color)
        if len(rgb) == 1:
            rgb = rgb * 3
        known = known and len(rgb) == 3
        if area(b):
            self.paints.append(dict(bbox=b, color=list(rgb), known=known))

    def stroke_path(self, *args):
        pass  # Rulings come from the existing edge converter, not this device.

    def fill_image(self, ctx, image, ctm, *args):
        rect = mupdf.fz_transform_rect(mupdf.FzRect(0, 0, 1, 1), mupdf.FzMatrix(ctm))
        self.paints.append(dict(bbox=list(pm.JM_py_from_rect(rect)), color=[], known=False))

    fill_image_mask = fill_image

    def fill_shade(self, ctx, shade, ctm, *args):
        self.paints.append(dict(bbox=[-1e10, -1e10, 1e10, 1e10], color=[], known=False))


def collect(page):
    """Derotated page-point inputs, scoped to this invocation, never a PDF cache."""
    if page.rotation:
        raise ValueError("Clip collection requires the existing derotated page")
    dev = ClipDevice()
    mupdf.fz_run_page(page.this, dev, mupdf.FzMatrix(), mupdf.FzCookie())
    mupdf.fz_close_device(dev)
    if dev.error:
        raise ValueError(dev.error)
    if dev.stack:
        raise ValueError("Unclosed table clip scope")
    grouped = {}
    for event in dev.events:
        if event["bbox"] is None:
            continue
        key = tuple(round(v, 3) for v in event["bbox"])
        record = grouped.setdefault(key, dict(index=len(grouped), bbox=event["bbox"], scoped_glyph_ids=set()))
        record["scoped_glyph_ids"].update(event["glyph_ids"])
    clips = [dict(c, scoped_glyph_ids=sorted(c["scoped_glyph_ids"])) for c in grouped.values()]
    return dict(glyphs=dev.glyphs, clips=clips, events=dev.events, backgrounds=dev.paints)
