"""Recovery authority: whole entry schema vs chart/diagram empty space."""
import pytest
from pymupdf import _table_append_structure as s
from pymupdf import _table_union as u


def material(cells, labels):
    chars = [dict(text=t,x0=x,x1=x+4,top=y,bottom=y+6) for t,x,y in labels]
    edges=[]
    for a,b,c,d in cells:
        edges.extend(dict(orientation='h',x0=a,x1=c,top=y,ruling_origin='vector') for y in (b,d))
        edges.extend(dict(orientation='v',x0=x,top=b,bottom=d,ruling_origin='vector') for x in (a,c))
    return chars,edges


def run(cells, labels, monkeypatch):
    chars,edges=material(cells,labels)
    monkeypatch.setattr(u,'CHARS',chars);monkeypatch.setattr(u,'EDGES',edges)
    monkeypatch.setattr(u,'_union_candidate_inside_picture',lambda *args: True)
    return u._union_admit_cell_groups(None,[cells])[1]


@pytest.mark.parametrize('labels',[('Name','Date'),('1','2'),('姓名','日期'),('الاسم','التاريخ')])
def test_repeated_blank_fields(labels,monkeypatch):
    cells=[(a,b,c,b+20) for b in (0,20) for a,c in ((0,40),(40,140))]
    entries=run(cells,[(labels[0],5,5),(labels[1],5,25)],monkeypatch)
    assert len(entries)==1 and entries[0].append_only


def test_disconnected_bar_compartments(monkeypatch):
    cells=[(a,b,c,b+20) for b in (0,40) for a,c in ((0,40),(40,140))]
    assert not run(cells,[('1',5,5),('2',5,45)],monkeypatch)


def test_chart_blank_rows_are_not_entry_records(monkeypatch):
    cells=[(a,b,c,b+20) for b in (0,20,40,60) for a,c in ((0,40),(40,140))]
    assert not run(cells,[('10',5,5),('20',5,65)],monkeypatch)


def test_variable_stacked_bar_boundaries(monkeypatch):
    cells=[(0,0,40,20),(40,0,140,20),(0,20,60,40),(60,20,140,40)]
    assert not run(cells,[('1',5,5),('2',5,25)],monkeypatch)


def test_diagram_border_strip_is_not_writable_field(monkeypatch):
    cells=[(0,0,8,20),(8,0,100,20),(0,20,8,100),(8,20,100,100)]
    assert not run(cells,[('Title',15,5),('Description',15,25)],monkeypatch)


def test_one_row_rescue_not_proven_but_existing_admission_preserved(monkeypatch):
    cells=[(0,0,40,20),(40,0,140,20)]
    chars,edges=material(cells,[('Name',5,5)])
    assert s.decide_append((0,0,140,20),[cells],s.PageEvidence(chars,edges)).approved
    assert not run(cells,[('Name',5,5)],monkeypatch)


def test_no_language_rule_cannot_separate_exact_geometric_lookalike(monkeypatch):
    # Explicit limitation: a graphic with exactly the same complete label and
    # writable-empty-field structure is not magically separable without context.
    cells=[(a,b,c,b+20) for b in (0,20) for a,c in ((0,40),(40,140))]
    assert run(cells,[('Series A',5,5),('Series B',5,25)],monkeypatch)


def test_transposed_form_keeps_existing_alignment_route(monkeypatch):
    cells=[(b,a,b+20,c) for b in (0,20) for a,c in ((0,40),(40,140))]
    entries=run(cells,[('Name',5,5),('Date',25,5)],monkeypatch)
    # Transposing puts two labels on one physical row; the existing alignment
    # admission succeeds, so the recovery-only branch must not claim authority.
    assert len(entries)==1 and not entries[0].append_only


def test_variable_row_heights(monkeypatch):
    cells=[(a,b,c,d) for b,d in ((0,20),(20,80)) for a,c in ((0,40),(40,140))]
    assert run(cells,[('Name',5,5),('Address',5,25)],monkeypatch)
