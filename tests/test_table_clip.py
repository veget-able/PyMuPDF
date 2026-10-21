"""Native painted-clip ownership without an HTML consumer."""

import pymupdf
from pymupdf._table_clip import ClipDevice, collect


def test_clip_scope_is_not_rectangular_text_containment():
    with pymupdf.open() as doc:
        page = doc.new_page(width=200, height=200)
        page.insert_text((20, 30), "INSIDE")
        page.insert_text((20, 50), "OUTSIDE")
        first, second = page.get_contents()
        stream = doc.xref_stream(first)
        doc.update_stream(first, b"q 10 160 100 30 re W n\n" + stream + b"\nQ")
        raw = collect(page)
        assert len(raw["clips"]) == 1
        scoped = "".join(raw["glyphs"][i]["text"] for i in raw["clips"][0]["scoped_glyph_ids"])
        assert scoped == "INSIDE"
        assert "OUTSIDE" in "".join(g["text"] for g in raw["glyphs"])


def test_nonrectangular_clip_defers():
    with pymupdf.open() as doc:
        p = doc.new_page(width=200, height=200)
        p.insert_text((20, 30), "ABC")
        (xref,) = p.get_contents()
        doc.update_stream(xref, b"q 0 0 m 200 0 l 200 200 l h W n\n" + doc.xref_stream(xref) + b"\nQ")
        raw = collect(p)
        assert not raw["clips"]
        assert not raw["glyphs"]


def test_soft_mask_scope_balances_and_defers():
    dev = ClipDevice()
    dev.begin_mask(None)
    assert dev.unsafe == 1
    dev.end_mask(None)
    assert dev.unsafe == 0 and len(dev.stack) == 1
    assert dev.events[0]["bbox"] is None
    dev.pop_clip(None)
    assert not dev.stack and dev.error is None


def test_live_soft_mask_does_not_escape_its_scope():
    with pymupdf.open() as doc:
        p = doc.new_page(width=200, height=200)
        p.insert_text((20, 30), "MASKED")
        p.insert_text((20, 50), "OUTSIDE")
        mask = doc.get_new_xref()
        doc.update_object(
            mask,
            "<</Type/XObject/Subtype/Form/BBox[0 0 200 200]/Resources<<>>/Group<</S/Transparency/CS/DeviceGray>>>>",
        )
        doc.update_stream(mask, b"1 g 0 0 200 200 re f")
        state = doc.get_new_xref()
        doc.update_object(state, f"<</Type/ExtGState/SMask<</S/Luminosity/G {mask} 0 R>>>>")
        resources = int(doc.xref_get_key(p.xref, "Resources")[1].split()[0])
        doc.xref_set_key(resources, "ExtGState", f"<</Mask {state} 0 R>>")
        first, _ = p.get_contents()
        doc.update_stream(first, b"q /Mask gs\n" + doc.xref_stream(first) + b"\nQ")
        raw = collect(p)
        assert "".join(g["text"] for g in raw["glyphs"]) == "OUTSIDE"
        assert all(not clip["scoped_glyph_ids"] for clip in raw["clips"])
        assert any(event["bbox"] is None for event in raw["events"])
