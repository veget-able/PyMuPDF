from copy import deepcopy
from types import SimpleNamespace as NS
from pymupdf._table_spans import resolve_spans
from pymupdf._table_word_geometry import page_word_geometry, glyph_cell_owners

def fixture():
 words=[(1,0,3,10,'[')]
 raw=[dict(type=0,lines=[dict(dir=[1,0],spans=[dict(chars=[dict(c='[',bbox=[1,7,3,9],origin=[1,8])])])])]
 p=NS(_refine_words_cache=words,_table_raw_blocks=raw,_span_text_spans_cache=[],_span_vertical_lines_cache=[])
 return p,words,[[[0,6,5,11]]]

def test_multiple_containing_cells_do_not_duplicate_glyph():
 p,w,cells=fixture();rows=resolve_spans(p,cells*2)
 assert all(c.text=='' for row in rows for c in row)
 assert glyph_cell_owners([(1,7,3,9)],[cells[0][0]]*2)==[0,1]

def test_source_geometry_cache_reuses_same_state_and_invalidates_new_raw_state():
 p,w,_=fixture();first=page_word_geometry(p,w)
 assert page_word_geometry(p,w) is first
 p._table_raw_blocks=deepcopy(p._table_raw_blocks)
 assert page_word_geometry(p,w) is not first

def test_existing_center_owner_is_preserved():
 p,w,_=fixture();rows=resolve_spans(p,[[[0,0,5,6]],[[0,6,5,11]]])
 assert [r[0].text for r in rows]==['[','']
