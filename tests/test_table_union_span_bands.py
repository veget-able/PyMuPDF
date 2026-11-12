"""Preserve the original cell grouping while narrowing the span scan."""
import math
import random
import types
import unittest

import pymupdf
from pymupdf import Rect
from pymupdf._table_union import (
    _union_cell_span_group_count,
    _union_span_multiplicity,
    _union_text_span_rects,
)


def full_scan(grid, spans):
    counts = []
    for row in grid:
        for cell in row:
            if cell is not None and not Rect(cell).is_empty:
                count = _union_cell_span_group_count(Rect(cell), spans)
                if count:
                    counts.append(count)
    return float(max(counts)) if counts else None


class SpanBandTests(unittest.TestCase):
    def assert_same(self, grid, spans):
        page = types.SimpleNamespace(_union_text_spans_cache=spans)
        before = [tuple(r) for r in spans]
        self.assertEqual(_union_span_multiplicity(page, grid), full_scan(grid, spans))
        self.assertIs(page._union_text_spans_cache, spans)
        self.assertEqual([tuple(r) for r in spans], before)

    def test_original_order_is_required(self):
        spans = [Rect(20, 5.5, 28, 6.5), Rect(0, -.5, 8, .5), Rect(0, 2.5, 8, 3.5)]
        cell = Rect(-1, -3, 40, 10)
        self.assertEqual(_union_cell_span_group_count(cell, spans), 2)
        self.assertEqual(_union_cell_span_group_count(cell, sorted(spans, key=lambda r: r.y0)), 1)
        self.assert_same([[cell]], spans)

    def test_inclusive_y_band_and_crossing_spans(self):
        for y in (-1., 11.):
            spans = [Rect(x, y-1, x+5, y+1) for x in (0, 10, 20)]
            self.assert_same([[Rect(0, 0, 40, 10)]], spans)
            self.assertEqual(full_scan([[Rect(0, 0, 40, 10)]], spans), 3.)
        self.assert_same([[Rect(0, 0, 10, 10)]], [Rect(-100, 4, 3, 6), Rect(7, 4, 100, 6)])

    def test_empty_duplicate_and_ragged_grids(self):
        spans = [Rect(0, 0, 6, 3)] * 2
        for grid in ([], [[]], [[None]], [[Rect(0, 0, 0, 10)]],
                     [[None, Rect(0, 0, 10, 10)], [Rect(20, 20, 30, 30)]]):
            self.assert_same(grid, spans)
            self.assert_same(grid, [])
        self.assertIsNone(_union_span_multiplicity(None, [[Rect(0, 0, 10, 10)]]))

    def test_nonfinite_inputs_keep_original_predicates(self):
        for number in (math.nan, math.inf, -math.inf):
            spans = [Rect(0, 0, 10, 5), Rect(20, number, 30, number)]
            grid = [[Rect(0, -1, 40, 10)]]
            # NaN does not compare equal in a snapshot; compare the decision only.
            page = types.SimpleNamespace(_union_text_spans_cache=spans)
            self.assertEqual(_union_span_multiplicity(page, grid), full_scan(grid, spans))
            self.assertEqual(_union_span_multiplicity(
                types.SimpleNamespace(_union_text_spans_cache=spans), [[Rect(0, number, 40, number)]]),
                full_scan([[Rect(0, number, 40, number)]], spans))

    def test_changed_list_and_rect_recomputed_without_an_index_cache(self):
        page = types.SimpleNamespace(_union_text_spans_cache=[Rect(0, 0, 5, 4)])
        grid = [[Rect(0, 0, 40, 10)]]
        self.assertEqual(_union_span_multiplicity(page, grid), 1.)
        page._union_text_spans_cache.append(Rect(20, 0, 25, 4))
        self.assertEqual(_union_span_multiplicity(page, grid), 2.)
        page._union_text_spans_cache[1].y0 = 30
        page._union_text_spans_cache[1].y1 = 34
        self.assertEqual(_union_span_multiplicity(page, grid), 1.)
        page._union_text_spans_cache = []
        self.assertIsNone(_union_span_multiplicity(page, grid))

    def test_randomized_full_scan_equivalence(self):
        rng = random.Random(20261112)
        for _ in range(1200):
            spans = []
            for _ in range(rng.randrange(60)):
                x, y = rng.uniform(-20, 120), rng.choice(range(-10, 110))
                spans.append(Rect(x, y, x+rng.uniform(.01, 40), y+rng.uniform(.01, 10)))
            rng.shuffle(spans)
            grid = [[None if rng.random()<.15 else Rect(x, y, x+rng.uniform(0, 80), y+rng.uniform(0, 30))
                     for x, y in [(rng.uniform(-20, 100), rng.uniform(-20, 100)) for _ in range(rng.randrange(8))]]
                    for _ in range(rng.randrange(5))]
            self.assert_same(grid, spans)

    def test_native_interleaved_image_input(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=200, height=200)
            page.insert_text((50, 140), 'UP', rotate=90)
            page.insert_image(Rect(120, 20, 150, 50), stream=b'P6\n1 1\n255\n'+bytes((255, 255, 255)))
            page.insert_text((50, 140-pymupdf.get_text_length('UP', fontsize=11)-2), 'DOWN', rotate=90)
            expected = [Rect(s['bbox']) for b in page.get_text('dict')['blocks']
                        for l in b.get('lines', []) for s in l['spans'] if s['text'].strip() and not Rect(s['bbox']).is_empty]
            self.assertEqual(_union_text_span_rects(page), expected)
            self.assertIs(_union_text_span_rects(page), page._union_text_spans_cache)
            self.assertEqual(_union_span_multiplicity(page, [[Rect(30, 80, 65, 145)]]),
                             full_scan([[Rect(30, 80, 65, 145)]], expected))


if __name__ == '__main__':
    unittest.main()
