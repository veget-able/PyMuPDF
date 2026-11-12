"""Retain native text boundaries while omitting image serialization for tables."""
import unittest
from unittest.mock import patch

import pymupdf
import pymupdf._table_refine as refine
import pymupdf._table_spans as spans
from pymupdf._table_text import _table_text_blocks


IMAGE = b'P6\n1 1\n255\n' + bytes((255, 255, 255))


def canonical_blocks(page, *, raw):
    return page.get_text('rawdict' if raw else 'dict')['blocks']


def fixture(doc, *, vertical=True, font='helv'):
    page = doc.new_page(width=200, height=200)
    for x in (35, 65, 105):
        page.draw_line((x, 80), (x, 145), width=0.5)
    for y in (80, 123, 145):
        page.draw_line((35, y), (105, y), width=0.5)
    rotation = 90 if vertical else 0
    start = (50, 140) if vertical else (25, 110)
    advance = pymupdf.get_text_length('UP', fontsize=11)
    end = (50, 140-advance-2) if vertical else (25+advance+2, 110)
    page.insert_text(start, 'UP', rotate=rotation)
    # An image between text paint operators affects native line grouping even
    # when its rectangle is elsewhere on the page.
    page.insert_image(pymupdf.Rect(120, 20, 150, 50), stream=IMAGE)
    page.insert_text(end, 'DOWN', rotate=rotation, fontname=font)
    page.insert_text((80, 105), '1')
    page.insert_text((80, 138), '2')
    return page


class TableTextBlockTests(unittest.TestCase):
    def test_native_layout_and_consumers_preserved(self):
        previous = pymupdf.TOOLS.set_small_glyph_heights()
        try:
            for small in (False, True):
                pymupdf.TOOLS.set_small_glyph_heights(small)
                for rotation in (0, 90, 180, 270):
                    for vertical in (False, True):
                        for font in ('helv', 'hebo'):
                            with self.subTest(small=small, rotation=rotation, vertical=vertical, font=font):
                                with pymupdf.open() as doc:
                                    page = fixture(doc, vertical=vertical, font=font)
                                    page.set_cropbox(pymupdf.Rect(10, 10, 190, 190))
                                    page.set_rotation(rotation)
                                    for raw in (False, True):
                                        expected = [{k: b[k] for k in ('type', 'bbox', 'lines')}
                                                    for b in canonical_blocks(page, raw=raw) if b['type'] == 0]
                                        self.assertEqual([{k: b[k] for k in ('type', 'bbox', 'lines')} for b in _table_text_blocks(page, raw=raw)], expected)
                                    for module, name, cache in (
                                        (refine, '_refine_rawdict_spans', None),
                                        (spans, '_span_text_spans', '_span_text_spans_cache'),
                                        (spans, '_span_vertical_text_lines', '_span_vertical_lines_cache'),
                                    ):
                                        function = getattr(module, name)
                                        if cache:
                                            setattr(page, cache, None)
                                        actual = function(page)
                                        if cache:
                                            self.assertIs(function(page), actual)
                                            setattr(page, cache, None)
                                        with patch.object(module, '_table_text_blocks', canonical_blocks):
                                            self.assertEqual(function(page), actual)
                                    self.assertTrue(any(b['type'] == 1 for b in canonical_blocks(page, raw=False)))
        finally:
            pymupdf.TOOLS.set_small_glyph_heights(previous)

    def test_interleaved_image_keeps_cell_text_separate(self):
        with pymupdf.open() as doc:
            page = fixture(doc)
            tables = page.find_tables(use_layout=False, refine=True).tables
            self.assertEqual(len(tables), 1)
            self.assertEqual(tables[0].to_html(),
                             '<table><tr><th>DOWN</th><th>1</th></tr><tr><td>UP</td><td>2</td></tr></table>')
            self.assertEqual(tables[0].extract(), [['DOWN', '1'], ['UP', '2']])

    def test_empty_and_image_only_pages(self):
        with pymupdf.open() as doc:
            page = doc.new_page()
            for image in (False, True):
                if image:
                    page.insert_image(pymupdf.Rect(10, 10, 40, 40), stream=IMAGE)
                for raw in (False, True):
                    self.assertEqual(_table_text_blocks(page, raw=raw), [])


if __name__ == '__main__':
    unittest.main()
