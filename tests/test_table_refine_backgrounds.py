"""Containment must retain size, overlap and duplicate-background semantics."""
import unittest

import pymupdf
from pymupdf._table_refine import _refine_cell_background_rects


class BackgroundRectTests(unittest.TestCase):
    def test_equal_area_duplicates_stay_in_order(self):
        rects = [pymupdf.Rect(0, 0, 10, 10), pymupdf.Rect(0, 0, 10, 10),
                 pymupdf.Rect(5, 0, 15, 10)]
        result = _refine_cell_background_rects(rects)
        self.assertEqual(list(map(id, result)), list(map(id, rects)))

    def test_strict_area_increase(self):
        child = pymupdf.Rect(0, 0, 10, 10)
        boundary = pymupdf.Rect(0, 0, 10.5, 10)
        larger = pymupdf.Rect(0, 0, 10.5001, 10)
        self.assertEqual(_refine_cell_background_rects([child, boundary]), [child, boundary])
        self.assertEqual(_refine_cell_background_rects([child, larger]), [larger])

    def test_partial_overlap_and_input_preservation(self):
        child = pymupdf.Rect(0, 0, 10, 10)
        partial = pymupdf.Rect(5, 0, 25, 10)
        covering = pymupdf.Rect(1, 0, 21, 10)
        snapshot = [tuple(x) for x in [child, partial, covering]]
        self.assertEqual(_refine_cell_background_rects([child, partial]), [child, partial])
        self.assertEqual(_refine_cell_background_rects([child, covering]), [covering])
        self.assertEqual([tuple(x) for x in [child, partial, covering]], snapshot)


if __name__ == '__main__':
    unittest.main()
