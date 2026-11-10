"""Raster rule input contracts; run directly with unittest (no test data)."""
import unittest
from unittest.mock import patch

import numpy as np
import pymupdf
from pymupdf import _table_raster as raster


def raster_pdf(ink=0, background=255):
    image = np.full((240, 320), background, np.uint8)
    for x in (20, 150, 290):
        image[20:222, x:x+2] = ink
    for y in (20, 120, 220):
        image[y:y+2, 20:292] = ink
    doc = pymupdf.open()
    page = doc.new_page(width=320, height=240)
    pix = pymupdf.Pixmap(pymupdf.csGRAY, 320, 240, image.tobytes(), False)
    page.insert_image(page.rect, stream=pix.tobytes('png'))
    page.insert_text((40, 65), 'Alpha')
    page.insert_text((180, 165), 'Beta')
    return doc


class RasterRuleTests(unittest.TestCase):
    def test_dark_rules_and_native_words(self):
        with raster_pdf() as doc:
            self.assertGreaterEqual(len(raster.detect_raster_table_lines(doc[0])), 6)

    def test_light_rules(self):
        with raster_pdf(255, 0) as doc:
            self.assertGreaterEqual(len(raster.detect_raster_table_lines(doc[0])), 6)

    def test_weak_rules(self):
        with raster_pdf(190, 255) as doc:
            self.assertGreaterEqual(len(raster.detect_raster_table_lines(doc[0])), 6)

    def test_no_words_no_admission(self):
        with raster_pdf() as doc:
            with patch.object(pymupdf.Page, 'get_text', return_value=[]):
                self.assertEqual(raster.detect_raster_table_lines(doc[0]), [])

    def test_text_needs_two_cells(self):
        component = ([(0, 0, 200, 0), (0, 100, 200, 100)],
                     [(0, 0, 0, 100), (100, 0, 100, 100), (200, 0, 200, 100)])
        self.assertEqual(raster._word_cell_count(component,
            [(20, 20, 40, 30), (45, 20, 65, 30)], tolerance=2), (2, 1))
        self.assertEqual(raster._word_cell_count(component,
            [(20, 20, 40, 30), (120, 20, 140, 30)], tolerance=2), (2, 2))

    def test_blank_image_rejected(self):
        self.assertEqual(raster._detect_grid_components(np.full((100, 100), 255, np.uint8),
                                                       scale=2, words=[]), [])

    def test_reuse_existing_images_and_textpage(self):
        with raster_pdf() as doc:
            page = doc[0]
            tp = page.get_textpage(flags=pymupdf.TEXT_PRESERVE_IMAGES)
            images = [b['bbox'] for b in tp.extractDICT()['blocks'] if b['type'] == 1]
            with patch.object(pymupdf.Page, 'get_textpage', side_effect=AssertionError('duplicate extraction')):
                with patch.object(pymupdf.Page, 'get_image_info', side_effect=AssertionError('duplicate image query')):
                    self.assertGreaterEqual(len(raster.detect_raster_table_lines(
                        page, textpage=tp, image_boxes=images)), 6)

    def test_image_free_skips_render_and_words(self):
        with pymupdf.open() as doc:
            page = doc.new_page()
            with patch.object(pymupdf.Page, 'get_text', side_effect=AssertionError('word extraction')):
                with patch.object(pymupdf.Page, 'get_pixmap', side_effect=AssertionError('render')):
                    self.assertEqual(raster.detect_raster_table_lines(page, image_boxes=[]), [])

    def test_pre_ocr_displaylist_and_live_words(self):
        with raster_pdf() as doc:
            page = doc[0]
            source = page.get_displaylist()
            page.insert_text((30, 110), 'Additional live text')
            with patch.object(pymupdf.Page, 'get_pixmap', side_effect=AssertionError('live pixels')):
                self.assertGreaterEqual(len(raster.detect_raster_table_lines(page, source=source)), 6)

    def test_page_edit_does_not_reuse_stale_cache(self):
        with raster_pdf() as doc:
            page = doc[0]
            self.assertGreaterEqual(len(raster.detect_raster_table_lines(page)), 6)
            with patch.object(pymupdf.Page, 'get_text', return_value=[]):
                self.assertEqual(raster.detect_raster_table_lines(page), [])

    def test_derotated_page_coordinates(self):
        for rotation in (90, 270):
            with raster_pdf() as doc:
                page = doc[0]
                page.set_rotation(rotation)
                page.remove_rotation()
                lines = raster.detect_raster_table_lines(page)
                self.assertGreaterEqual(len(lines), 6)
                self.assertTrue(all(page.rect.contains(pymupdf.Point(p)) for line in lines for p in line))

    def test_cropped_image_coordinates(self):
        with raster_pdf() as doc:
            page = doc[0]
            page.set_cropbox(pymupdf.Rect(10, 10, 310, 230))
            lines = raster.detect_raster_table_lines(page)
            self.assertGreaterEqual(len(lines), 6)
            self.assertTrue(all(page.rect.contains(pymupdf.Point(p)) for line in lines for p in line))

    def test_optional_opencv(self):
        import sys
        with raster_pdf() as doc:
            with patch.dict(sys.modules, {'cv2': None}):
                self.assertEqual(raster.detect_raster_table_lines(doc[0]), [])

    def test_pixels_not_modified(self):
        image = np.full((240, 320), 255, np.uint8)
        original = image.copy()
        raster._detect_grid_components(image, scale=2, words=[])
        np.testing.assert_array_equal(image, original)

    def test_occurrence_dedup_and_small_image_filter(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=320, height=240)
            self.assertEqual(raster._image_regions(page, [(0, 0, 10, 10),
                (10, 10, 310, 230), (10, 10, 310, 230)]), [pymupdf.Rect(10, 10, 310, 230)])


if __name__ == '__main__':
    unittest.main()
