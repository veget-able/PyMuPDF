"""Normal-table counterexamples and geometric controls, without model inference."""
from copy import deepcopy
from itertools import permutations
import pytest
from pymupdf import _table_union as u


def char(x,top,bottom,text='1'):
 return dict(x0=x,x1=x+1,top=top,bottom=bottom,text=text)

def decide(monkeypatch,grid,chars):
 before=deepcopy((grid,chars));monkeypatch.setattr(u,'CHARS',chars)
 answer=u._union_grid_has_aligned_text(grid)
 assert (grid,chars)==before
 return answer

def numeric_spanning():
 # The numeric spanning header and two body rows contain real empty cells.
 grid=[[(0,0,60,20),None,None],[(0,20,20,40),(20,20,40,40),(40,20,60,40)],[(0,40,20,60),(20,40,40,60),(40,40,60,60)]]
 chars=[char(2,4,14,'2026'),char(2,24,34,'1'),char(42,24,34,'2'),char(2,44,54,'3'),char(42,44,54,'4')]
 return grid,chars

def irregular():
 return [[(0,y,20,y+20),None,(40,y,60,y+20)] for y in [0,20,40]]

def test_numeric_spanning_header_with_blank_cells(monkeypatch):
 grid,chars=numeric_spanning();monkeypatch.setattr(u,'CHARS',chars)
 assert u._union_grid_has_2d_content_support(grid)
 assert decide(monkeypatch,grid,chars)

def test_numeric_rowspan_with_blank_cell(monkeypatch):
 grid=[[(0,0,20,40),(20,0,40,20),(40,0,60,20)],[None,(20,20,40,40),(40,20,60,40)]]
 chars=[char(2,3,13,'2026'),char(22,3,13),char(22,23,33,'2'),char(42,23,33,'3')]
 assert decide(monkeypatch,grid,chars)

@pytest.mark.parametrize('top_difference',[0,4,8])
def test_same_bottom_mixed_glyph_heights(monkeypatch,top_difference):
 chars=[char(2,2,14,'A'),char(42,2+top_difference,14,'1'),char(2,22,34,'B'),char(42,22+top_difference,34,'2')]
 assert decide(monkeypatch,irregular(),chars)

@pytest.mark.parametrize('scale',[0.5,1,2,4])
def test_numeric_geometry_is_scale_independent(monkeypatch,scale):
 grid,chars=numeric_spanning();grid=[[tuple(v*scale for v in c) if c else None for c in row] for row in grid]
 chars=[{k:(v*scale if k in ['x0','x1','top','bottom'] else v) for k,v in ch.items()} for ch in chars]
 assert decide(monkeypatch,grid,chars)

def test_letters_are_not_required_for_same_geometry(monkeypatch):
 for texts in [('A','B','C','D'),('1','2','3','4'),('١','٢','٣','٤')]:
  chars=[char(x,y,y+10,t) for (x,y),t in zip([(2,2),(42,2),(2,22),(42,22)],texts)]
  assert decide(monkeypatch,irregular(),chars)

def test_minor_vertical_overlap_is_not_row_alignment(monkeypatch):
 chars=[char(2,1,7,'A'),char(42,6,12,'1'),char(2,21,27,'B'),char(42,26,32,'2')]
 assert not decide(monkeypatch,irregular(),chars)

def test_tall_glyph_does_not_bridge_disjoint_text_rows(monkeypatch):
 grid=irregular()
 # Two lines inside the same left cell with one tall glyph in the right cell
 # must not count as two aligned rows. The second grid row is empty.
 chars=[char(2,1,7,'A'),char(2,11,17,'B'),char(42,1,17,'1')]
 for order in permutations(chars):assert not decide(monkeypatch,grid,list(order))

def test_order_invariance_of_mixed_heights(monkeypatch):
 chars=[char(2,2,14,'A'),char(42,6,14,'1'),char(2,22,34,'B'),char(42,26,34,'2')]
 for order in permutations(chars):assert decide(monkeypatch,irregular(),list(order))

def test_empty_and_invalid_glyphs_cannot_supply_alignment(monkeypatch):
 assert not decide(monkeypatch,irregular(),[char(2,4,4),char(42,4,4),char(2,24,24),char(42,24,24)])
