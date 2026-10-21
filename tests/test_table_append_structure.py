"""Independent-region approval; no GT or experiment paths."""
import pytest
from pymupdf import _table_append_structure as mod

def char(text, x, y, width=5, height=8):
    return dict(text=text,x0=x,x1=x+width,top=y,bottom=y+height)


def edges(cells, origin='vector'):
    out=[]
    for a,b,c,d in cells:
        out.extend([dict(orientation='h',x0=a,x1=c,top=y,bottom=y,ruling_origin=origin) for y in (b,d)])
        out.extend([dict(orientation='v',x0=x,x1=x,top=b,bottom=d,ruling_origin=origin) for x in (a,c)])
    return out


def decide(grid, chars, *, origin='vector', owner=None, sides=None):
    cells=[c for row in grid for c in row if c is not None]
    box=[min(c[0] for c in cells),min(c[1] for c in cells),max(c[2] for c in cells),max(c[3] for c in cells)]
    return mod.decide_append(box,grid,mod.PageEvidence(chars,edges(cells,origin) if sides is None else sides),external_owner=owner)


@pytest.mark.parametrize('origin',['vector','raster'])
@pytest.mark.parametrize('label',['A','金額','قيمة','25'])
def test_records(origin,label):
    grid=[[(0,0,50,20),(50,0,100,20)],[(0,20,50,40),(50,20,100,40)]]
    result=decide(grid,[char(label,x,y) for x in (10,60) for y in (5,25)],origin=origin)
    assert result.rule=='ruled_records'


@pytest.mark.parametrize('origin',['vector','raster'])
def test_sparse_single_row_form(origin):
    assert decide([[(0,0,50,20),(50,0,100,20)]],[char('Label',5,5)],origin=origin).rule=='ruled_form'


def test_single_record():
    assert decide([[(0,0,50,20),(50,0,100,20)]],[char('A',5,5),char('B',65,5)]).rule=='single_record'


def test_single_column():
    assert decide([[(0,0,50,20)],[(0,20,50,40)]],[char('A',5,5),char('B',5,25)]).rule=='single_column'


def test_merged_header():
    grid=[[(0,0,100,20),None],[(0,20,50,40),(50,20,100,40)]]
    assert decide(grid,[char('Header',40,5),char('A',10,25),char('B',60,25)]).rule=='spanning_record'


def test_word_fragment_not_fields():
    grid=[[(0,0,50,20),(50,0,100,20)]]
    assert not decide(grid,[char('13040',25,5,width=25),char('.19',50,5,width=15)]).approved


@pytest.mark.parametrize('origin',[None,'user_line','synthetic'])
def test_unproven_edges_not_approval(origin):
    assert not decide([[(0,0,50,20),(50,0,100,20)]],[char('A',5,5),char('B',65,5)],origin=origin).approved


def test_empty_grid_not_table():
    assert not decide([[(0,0,50,20),(50,0,100,20)]],[]).approved


def test_external_component_not_independent_table():
    assert not decide([[(0,0,50,20),(50,0,100,20)]],[char('A',5,5),char('B',65,5)],owner='enclosing_math_delimiters').approved


def test_missing_material_is_not_approval():
    assert not mod.decide_append((0,0,100,20),[],None).approved


def test_partial_rules_require_repeated_fields():
    grid=[[(0,0,50,20),(50,0,100,20)],[(0,20,50,40),(50,20,100,40)]]
    e=[v for v in edges([c for row in grid for c in row]) if v['orientation']=='h']
    assert decide(grid,[char('A',x,y) for x in (10,60) for y in (5,25)],sides=e).rule=='partially_ruled_records'
    assert not decide(grid,[char('A',10,5),char('B',60,5)],sides=e).approved


def test_half_open_membership_and_order():
    m=mod.PageEvidence([char('a',45,5,width=10),char('b',5,5)],[])
    assert m.members((0,0,50,20))==[1]
    assert m.members((50,0,100,20))==[0]
    m.centers=None
    assert m.members((0,0,50,20))==[1]
    assert m.members((50,0,100,20))==[0]


def test_overlap_does_not_duplicate_content():
    grid=[[(0,0,60,20),(40,0,100,20)]]
    assert not decide(grid,[char('A',45,5),char('B',70,5)]).approved


@pytest.mark.parametrize('scale',[.5,1,2])
def test_translated_scaled_structure(scale):
    cells=[(0,0,50,20),(50,0,100,20)]
    transform=lambda c:tuple(v*scale+(100 if i%2==0 else 200) for i,v in enumerate(c))
    cs=[transform(c) for c in cells]
    chars=[char('A',105,205,width=2,height=4),char('B',100+60*scale,205,width=2,height=4)]
    material=mod.PageEvidence(chars,edges(cs),snap_x=3*scale,snap_y=3*scale)
    assert mod.decide_append(transform((0,0,100,20)),[cs],material).approved
