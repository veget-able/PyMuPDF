"""Native candidate admission remains usable without a structured runtime."""
import unittest
import pymupdf


class NativeAdmissionScopeTests(unittest.TestCase):
    def test_ruled_table_with_native_union_on_rotated_pages(self):
        for rotation, crop in ((0, False), (90, False), (270, True)):
            with self.subTest(rotation=rotation, crop=crop):
                doc = pymupdf.open()
                page = doc.new_page(width=400, height=400)
                for x in (60, 180, 300):
                    page.draw_line((x, 60), (x, 180))
                for y in (60, 100, 140, 180):
                    page.draw_line((60, y), (300, y))
                for y, values in ((85, ('Name', 'Amount')),
                                  (125, ('One', '123')),
                                  (165, ('Two', '456'))):
                    for x, value in zip((70, 190), values):
                        page.insert_text((x, y), value)
                if crop:
                    page.set_cropbox(pymupdf.Rect(20, 20, 380, 380))
                page.set_rotation(rotation)
                raw = doc.tobytes()
                doc.close()
                with pymupdf.open(stream=raw, filetype='pdf') as doc:
                    finder = doc[0].find_tables(union=True, refine=True,
                                                use_layout=False)
                    self.assertEqual(len(finder.tables), 1)
                    values = [value for row in finder.tables[0].extract()
                              for value in row if value]
                    self.assertCountEqual(values,
                                          ['Name', 'Amount', 'One', '123', 'Two', '456'])


if __name__ == '__main__':
    unittest.main()
