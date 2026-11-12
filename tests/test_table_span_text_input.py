"""Text-only input retains span records, live cache and default image extraction."""
import unittest

import pymupdf
from pymupdf._table_spans import _span_text_spans


class PageInput:
    def __init__(self,data):self.data,self.calls=data,[]
    def get_text(self,kind,**kwargs):
        self.calls.append((kind,kwargs))
        return self.data


class SpanTextTests(unittest.TestCase):
    def test_order_duplicates_filter_and_cache(self):
        page=PageInput({'blocks':[{'type':1,'image':b'ignored'},{'type':0,'lines':[{'spans':[
            {'text':' A ','bbox':[0,0,10,10]}, {'text':' aa ','bbox':[0,0,10,10]},
            {'text':' aa ','bbox':[0,0,10,10]}, {'text':'日本語','bbox':[10,0,20,10]},
            {'text':'empty','bbox':[0,0,0,10]}, {'text':'missing'}]}]}]})
        result=_span_text_spans(page)
        self.assertEqual([(tuple(rect),text) for rect,text in result],
                         [((0.,0.,10.,10.),'aa'),((0.,0.,10.,10.),'aa'),((10.,0.,20.,10.),'日本語')])
        self.assertIs(_span_text_spans(page),result)
        self.assertEqual(page.calls,[('dict',{'flags':pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES})])

    def test_eligible_geometry_errors_propagate(self):
        with self.assertRaises((TypeError,ValueError)):
            _span_text_spans(PageInput({'blocks':[{'lines':[{'spans':[{'text':'AB','bbox':['invalid',0,5,5]}]}]}]}))

    def test_native_text_around_image(self):
        with pymupdf.open() as doc:
            page=doc.new_page(width=200,height=200)
            page.insert_text((20,30),'HEAD')
            page.insert_image(pymupdf.Rect(20,40,100,60),stream=b'P6\n1 1\n255\n'+bytes((255,255,255)))
            page.insert_text((20,80),'ROW')
            page.insert_text((140,160),'VERTICAL',rotate=90)
            raw=page.get_text('dict')
            self.assertTrue(any(block.get('type')==1 for block in raw['blocks']))
            expected=[(tuple(span['bbox']),span['text'].strip()) for block in raw['blocks']
                      for line in block.get('lines',[]) for span in line['spans'] if len(span['text'].strip())>=2]
            self.assertEqual([(tuple(rect),text) for rect,text in _span_text_spans(page)],expected)
            self.assertTrue(any(block.get('type')==1 for block in page.get_text('dict')['blocks']))


if __name__=='__main__':unittest.main()
