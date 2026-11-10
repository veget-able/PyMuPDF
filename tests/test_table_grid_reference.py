"""Protect text separation when a ruled grid replaces a layout grid."""

import unittest
from unittest.mock import patch

import pymupdf
import pymupdf._table_union as union


def entry(columns):
    grid = [
        [(100 * col / columns, 10 * row,
          100 * (col + 1) / columns, 10 * (row + 1))
         for col in range(columns)]
        for row in range(2)
    ]
    return pymupdf.Rect(0, 0, 100, 20), grid


class TextSeparationTests(unittest.TestCase):
    def decide(self, primary_columns, candidate_columns, values, gate=True):
        with patch.object(union, "_union_span_multiplicity", side_effect=values) as scan:
            refs, _ = union._union_one_to_one_grid_refs(
                [entry(primary_columns)], [entry(candidate_columns)],
                iou_threshold=0.9, page=object(), span_mult_gate=gate,
                span_mult_threshold=3.0,
            )
            return bool(refs), scan.call_count

    def test_merged_text_groups_reject_coarser_grid(self):
        self.assertEqual(self.decide(4, 2, [2.0, 1.0]), (False, 2))

    def test_coarser_empty_columns_can_be_removed(self):
        self.assertEqual(self.decide(4, 2, [1.0, 1.0]), (True, 2))

    def test_equal_column_count_keeps_original_gate(self):
        self.assertEqual(self.decide(4, 4, [2.0]), (True, 1))

    def test_finer_candidate_keeps_original_gate(self):
        self.assertEqual(self.decide(2, 4, [2.0]), (True, 1))

    def test_absolute_undersegmentation_still_rejected(self):
        self.assertEqual(self.decide(4, 2, [3.0]), (False, 1))

    def test_unknown_source_retains_previous_decision(self):
        self.assertEqual(self.decide(4, 2, [None, None]), (True, 2))

    def test_disabled_gate_does_not_scan(self):
        self.assertEqual(self.decide(4, 2, [], gate=False), (True, 0))

    def test_ambiguous_matches_not_replaced(self):
        with patch.object(union, "_union_span_multiplicity") as scan:
            result = union._union_one_to_one_grid_refs(
                [entry(4)], [entry(2), entry(2)],
                iou_threshold=0.9, page=object(), span_mult_gate=True,
                span_mult_threshold=3.0,
            )
            self.assertEqual(result, ({}, set()))
            scan.assert_not_called()

    def actual_text(self, filled_columns):
        with pymupdf.open() as doc:
            page = doc.new_page(width=300, height=120)
            for row in range(2):
                for col in filled_columns:
                    page.insert_text((10 + 70 * col, 20 + 50 * row), f"V{row}{col}")
            bounds = pymupdf.Rect(0, 0, 280, 100)
            primary = (bounds, [
                [(70 * col, 50 * row, 70 * (col + 1), 50 * (row + 1))
                 for col in range(4)]
                for row in range(2)
            ])
            candidate = (bounds, [
                [(140 * col, 50 * row, 140 * (col + 1), 50 * (row + 1))
                 for col in range(2)]
                for row in range(2)
            ])
            refs, _ = union._union_one_to_one_grid_refs(
                [primary], [candidate], iou_threshold=0.9, page=page,
                span_mult_gate=True, span_mult_threshold=3.0,
            )
            return bool(refs)

    def test_actual_pdf_separated_values_are_preserved(self):
        self.assertFalse(self.actual_text(range(4)))

    def test_actual_pdf_empty_extra_columns_can_be_removed(self):
        self.assertTrue(self.actual_text([0, 2]))


if __name__ == "__main__":
    unittest.main()
