"""The refinement producer retains eligible text, geometry, order and cache."""
import unittest
from unittest.mock import patch

import pymupdf

from pymupdf._table_refine import _refine_page_words, _refine_rawdict_spans


class PageInput:
    def __init__(self, lines, words=()):
        self.data = {'rawdict': {'blocks': [{'type': 0, 'lines': lines}]}, 'words': list(words)}
        self.calls = []
        self.options = []

    def get_text(self, kind, **kwargs):
        self.calls.append(kind)
        self.options.append(kwargs)
        return self.data[kind]


def line(text, direction, wmode=0, bbox=(0, 0, 5, 10)):
    return {'dir': direction, 'wmode': wmode,
            'spans': [{'bbox': bbox, 'chars': [{'c': c} for c in text]}]}


class RotatedSpanTests(unittest.TestCase):
    def setUp(self):
        from pymupdf._table_text import _table_text_blocks
        def blocks(page, *, raw):
            if isinstance(page, PageInput):
                return page.get_text('rawdict', flags=pymupdf.TEXTFLAGS_RAWDICT)['blocks']
            return _table_text_blocks(page, raw=raw)
        fixture = patch('pymupdf._table_refine._table_text_blocks', side_effect=blocks)
        fixture.start()
        self.addCleanup(fixture.stop)

    def test_eligible_spans_keep_text_geometry_and_order(self):
        page = PageInput([line('horizontal', (1, 0)), line(' 縦 ', (0, 1)),
                          line('  ', (0, -1)), line('mode', (1, 0), wmode=1),
                          line('missing', None)])
        result = _refine_rawdict_spans(page)
        self.assertEqual([item['text'] for item in result], [' 縦 ', 'mode'])
        self.assertEqual([item['bbox'] for item in result], [[0., 0., 5., 10.]] * 2)
        self.assertEqual([item['dir'] for item in result], [(0, 1), (1, 0)])
        self.assertEqual([item['wmode'] for item in result], [0, 1])

    def test_word_substitution_and_cache(self):
        page = PageInput([line('vertical', (0, 1))],
                         [(1, 1, 3, 3, 'fragment'), (20, 1, 25, 5, 'keep')])
        result = _refine_page_words(page)
        self.assertEqual(result, [(0., 0., 5., 10., 'vertical'), (20., 1., 25., 5., 'keep')])
        self.assertIs(_refine_page_words(page), result)
        self.assertEqual(page.calls, ['words', 'rawdict'])
        self.assertEqual(page.options, [{}, {'flags': pymupdf.TEXTFLAGS_RAWDICT}])

    def test_native_image_and_vertical_text(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=200, height=200)
            page.insert_image(pymupdf.Rect(40, 80, 65, 160),
                              stream=b'P6\n1 1\n255\n' + bytes((255, 255, 255)))
            page.insert_text((80, 150), 'Horizontal')
            page.insert_text((50, 150), 'VERTICAL', rotate=90)
            raw = page.get_text('rawdict')
            self.assertTrue(any(block.get('type') == 1 for block in raw['blocks']))
            vertical_line = next(line for block in raw['blocks'] if block.get('type') == 0
                                 for line in block['lines'] if abs(line['dir'][1]) > abs(line['dir'][0]))
            span = vertical_line['spans'][0]
            self.assertEqual(_refine_rawdict_spans(page), [{
                'bbox': list(map(float, span['bbox'])), 'text': 'VERTICAL',
                'dir': vertical_line['dir'], 'wmode': vertical_line['wmode']}])
            self.assertTrue(any(block.get('type') == 1 for block in page.get_text('rawdict')['blocks']))

    def test_eligible_geometry_errors_propagate(self):
        with self.assertRaises(ValueError):
            _refine_page_words(PageInput([line('vertical', (0, 1), bbox=('invalid', 0, 5, 10))]))


if __name__ == '__main__':
    unittest.main()
