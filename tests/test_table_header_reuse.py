"""A reused text-grid decision must follow live text and preserve grid shape."""
import unittest
from unittest.mock import patch

from pymupdf import table
from pymupdf._table_headers import HeaderRegion
from pymupdf._table_spans import SpanCell


class HeaderReuseTests(unittest.TestCase):
    def grid(self, rows):
        return [[SpanCell(bbox=None, text=text, colspan=1, rowspan=1)
                 for text in row] for row in rows]

    def test_live_text_and_row_boundaries(self):
        grid = self.grid([['A', 'B'], ['1', '2']])
        decisions = {}
        with patch.object(table, 'find_header_region', wraps=table.find_header_region) as finder:
            first = table._refine_header_region(grid, decisions)
            self.assertEqual(table._refine_header_region(self.grid([['A', 'B'], ['1', '2']]), decisions), first)
            self.assertEqual(finder.call_count, 1)
            grid[1][0].text = 'changed'
            table._refine_header_region(grid, decisions)
            self.assertEqual(finder.call_count, 2)
            table._refine_header_region(self.grid([['A'], ['B', 'changed', '2']]), decisions)
            self.assertEqual(finder.call_count, 3)
            table._refine_header_region(grid, {})
            self.assertEqual(finder.call_count, 4)

    def test_failed_decision_is_not_reused(self):
        grid = self.grid([['A', 'B']])
        decisions = {}
        with patch.object(table, 'find_header_region', side_effect=[ValueError('failure'), HeaderRegion(1, ())]) as finder:
            with self.assertRaises(ValueError):
                table._refine_header_region(grid, decisions)
            self.assertFalse(decisions)
            self.assertEqual(table._refine_header_region(grid, decisions), HeaderRegion(1, ()))
            self.assertEqual(finder.call_count, 2)


if __name__ == '__main__':
    unittest.main()
