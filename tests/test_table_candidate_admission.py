"""Portable content-topology controls for picture-contained candidate admission."""
from copy import deepcopy
from pymupdf import _table_union as union

def glyph(x,y,text):return dict(x0=x,x1=x+1,top=y,bottom=y+1,text=text)
def grid():return [[(10*c,10*r,10*(c+1),10*(r+1)) for c in range(3)] for r in range(3)]
def test_numeric_sparse_rectangular_grid(monkeypatch):
 monkeypatch.setattr(union,'CHARS',[glyph(2,2,'1'),glyph(22,22,'7')]);assert union._union_grid_has_aligned_text(grid())
def test_empty_grid_is_not_content(monkeypatch):
 monkeypatch.setattr(union,'CHARS',[]);assert not union._union_grid_has_aligned_text(grid())
def test_complete_single_column_and_spanning_cells(monkeypatch):
 monkeypatch.setattr(union,'CHARS',[glyph(2,2,'1'),glyph(2,12,'7')]);assert union._union_grid_has_aligned_text([[(0,0,10,10)],[(0,10,10,20)]])
 monkeypatch.setattr(union,'CHARS',[glyph(2,2,'Title'),glyph(2,12,'1'),glyph(12,12,'2')]);assert union._union_grid_has_aligned_text([[(0,0,20,10),None],[(0,10,10,20),(10,10,20,20)]])
def test_sparse_labelled_rows_reuse_real_cell_alignment(monkeypatch):
 cells=grid();cells[0][1]=None;chars=[glyph(2,2,'항목'),glyph(22,2,'값'),glyph(2,12,'A'),glyph(22,12,'3')];before=deepcopy((cells,chars));monkeypatch.setattr(union,'CHARS',chars);assert union._union_grid_has_aligned_text(cells);assert (cells,chars)==before
 def shifted():
  return [glyph(2,2,'A'),glyph(22,7,'B'),glyph(2,12,'C'),glyph(22,17,'D')]
 monkeypatch.setattr(union,'CHARS',shifted());assert not union._union_grid_has_aligned_text(cells)
def test_character_membership_is_half_open(monkeypatch):
 monkeypatch.setattr(union,'CHARS',[glyph(30,2,'A'),glyph(30,12,'B')]);assert not union._union_grid_has_aligned_text(grid())
