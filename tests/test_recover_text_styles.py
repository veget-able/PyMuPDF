import pymupdf


UNDERLINE = pymupdf.mupdf.FZ_STEXT_UNDERLINE


def _styled_spans(page):
    flags = pymupdf.TEXT_ACCURATE_BBOXES | pymupdf.TEXT_COLLECT_STYLES
    return [
        span
        for block in page.get_text("dict", flags=flags)["blocks"]
        if block.get("type") == 0
        for line in block["lines"]
        for span in line["spans"]
    ]


def test_mupdf_decorator_endpoints_use_character_centres():
    doc = pymupdf.open()
    page = doc.new_page()
    fontsize = 20
    x = 72
    page.insert_text((x, 100), "General", fontsize=fontsize)
    x0 = x + pymupdf.get_text_length("Gen", fontsize=fontsize)
    x1 = x + pymupdf.get_text_length("Gener", fontsize=fontsize)
    page.draw_rect(
        pymupdf.Rect(x0, 101, x1, 102),
        color=None,
        fill=(0, 0, 0),
        overlay=True,
    )

    doc = pymupdf.open(stream=doc.tobytes(), filetype="pdf")
    spans = _styled_spans(doc[0])
    assert "".join(span["text"] for span in spans) == "General"
    assert "".join(
        span["text"] for span in spans if span["char_flags"] & UNDERLINE
    ) == "er"
    page = doc[0]
    textpage = page.get_textpage(flags=pymupdf.TEXT_COLLECT_STYLES)
    blocks = textpage.extractDICT()["blocks"]
    pymupdf.recover_text_styles(page, blocks, textpage=textpage)
    spans = [
        span
        for block in blocks
        if block.get("type") == 0
        for line in block["lines"]
        for span in line["spans"]
    ]
    assert "".join(
        span["text"] for span in spans if span["char_flags"] & UNDERLINE
    ) == "er"
    assert all(
        span.get("recovered_style")
        for span in spans
        if span["char_flags"] & UNDERLINE
    )


def test_recover_text_styles_generates_metadata_not_markup():
    doc = pymupdf.open()
    page = doc.new_page()
    fontsize = 20
    x = 72
    page.insert_text((x, 100), "General", fontsize=fontsize)
    x0 = x + pymupdf.get_text_length("Gen", fontsize=fontsize)
    x1 = x + pymupdf.get_text_length("Gener", fontsize=fontsize)
    page.draw_line((x0, 102), (x1, 102), width=0.8, overlay=True)

    doc = pymupdf.open(stream=doc.tobytes(), filetype="pdf")
    page = doc[0]
    textpage = page.get_textpage(flags=pymupdf.TEXT_COLLECT_STYLES)
    blocks = textpage.extractDICT()["blocks"]
    pymupdf.recover_text_styles(page, blocks, textpage=textpage)
    spans = [
        span
        for block in blocks
        if block.get("type") == 0
        for line in block["lines"]
        for span in line["spans"]
    ]

    assert "".join(span["text"] for span in spans) == "General"
    assert "".join(
        span["text"] for span in spans if span["char_flags"] & UNDERLINE
    ) == "er"
    assert all("<u>" not in span["text"] for span in spans)


def test_recover_text_styles_generates_script_metadata():
    # Detection now lives in MuPDF's line assembly, so draw real text:
    # a full-size H and O with a reduced, lowered 2 between them (H2O).
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "H", fontsize=20)
    page.insert_text((85, 105), "2", fontsize=10)
    page.insert_text((92, 100), "O", fontsize=20)
    blocks = pymupdf.recover_text_styles(page)
    spans = [
        span
        for block in blocks
        for line in block.get("lines", ())
        for span in line.get("spans", ())
    ]
    scripts = {span["text"].strip(): span.get("script") for span in spans}
    assert scripts.get("2") == "subscript"
    assert scripts.get("H") is None
    assert scripts.get("O") is None


def test_recover_text_styles_does_not_infer_script_from_ocr_geometry():
    doc = pymupdf.open()
    page = doc.new_page()
    blocks = [
        {
            "type": 0,
            "lines": [
                {
                    "spans": [
                        {
                            "text": "Heading",
                            "size": 10,
                            "origin": (72, 95),
                            "flags": 0,
                            "font": "GlyphLessFont",
                            "char_flags": 0,
                        },
                        {
                            "text": "body",
                            "size": 20,
                            "origin": (72, 100),
                            "flags": 0,
                            "font": "GlyphLessFont",
                            "char_flags": 0,
                        },
                    ]
                }
            ],
        }
    ]

    pymupdf.recover_text_styles(page, blocks)
    assert all(
        "script" not in span for span in blocks[0]["lines"][0]["spans"]
    )
