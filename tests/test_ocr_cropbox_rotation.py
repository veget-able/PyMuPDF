"""Offset CropBoxes retain their visible content through rotation removal."""
import pytest
import pymupdf


@pytest.mark.parametrize("angle", [90, 180, 270])
@pytest.mark.parametrize("offset", [False, True])
def test_offset_cropbox_render_is_preserved(angle, offset):
    doc = pymupdf.open()
    page = doc.new_page(width=400, height=500)
    page.insert_text((115, 175), "KEEP OCR INPUT", fontsize=18)
    page.draw_rect(pymupdf.Rect(130, 200, 220, 240), fill=(0.2, 0.6, 0.8))
    if offset:
        page.set_cropbox(pymupdf.Rect(80, 120, 340, 430))
    page.set_rotation(angle)
    before, rect = page.get_pixmap(dpi=144), pymupdf.Rect(page.rect)
    page.remove_rotation()
    after = page.get_pixmap(dpi=144)
    assert page.rotation == 0 and page.rect == rect
    assert before.samples == after.samples
    assert "KEEP OCR INPUT" in page.get_text()


@pytest.mark.parametrize("angle", [90, 180, 270])
def test_offset_crop_annotations_and_links(angle):
    doc = pymupdf.open()
    page = doc.new_page(width=400, height=500)
    page.insert_text((115, 175), "KEEP OCR INPUT", fontsize=18)
    page.add_rect_annot(pymupdf.Rect(110, 150, 290, 190)).update()
    page.insert_link(dict(kind=pymupdf.LINK_URI,
                          **{"from": pymupdf.Rect(110, 150, 290, 190)},
                          uri="https://example.com/ocr"))
    page.set_cropbox(pymupdf.Rect(80, 120, 340, 430))
    page.set_rotation(angle)
    page = doc.reload_page(page)
    # Draft-c itself changes rectangular annotation AP pixels at 90/270.
    # Check the page pixels and annotation/link geometry independently of
    # that pre-existing appearance-stream behavior.
    before = page.get_pixmap(dpi=144, annots=False)
    expected_annot = next(page.annots()).rect * page.rotation_matrix
    link = page.get_links()[0]
    expected_link = pymupdf.Rect(link["from"])
    # get_links already returns rotated visible-page coordinates.
    page.remove_rotation()
    after_link = pymupdf.Rect(page.get_links()[0]["from"])
    assert all(abs(a-b) < 1e-3 for a, b in zip(expected_link, after_link))
    after_annot = next(page.annots()).rect
    assert all(abs(a-b) < 1e-3 for a, b in zip(expected_annot, after_annot))
    assert before.samples == page.get_pixmap(dpi=144, annots=False).samples
