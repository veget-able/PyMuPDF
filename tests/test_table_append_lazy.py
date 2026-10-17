"""Call lifetime, lazy authority, and immutable c07 decision parity."""
from types import SimpleNamespace

import pytest
from pymupdf import table, _table_union as u, _table_append_context as c
from pymupdf import _table_append_structure as s, _table_component_context as components





def entry(box, context, index=0):
    return u._TableGridEntry(u.pymupdf.Rect(box), [[box]], {},
                             append_context=context, append_index=index)


KW = dict(page=None, grid_ref=False, grid_ref_iou=.9,
          span_mult_gate=False, span_mult_threshold=3)


@pytest.mark.parametrize('branch', ['grid_ref', 'split', 'ambiguous'])
def test_non_append_never_evaluates(branch, monkeypatch):
    class Never:
        def decide(self, index):
            pytest.fail('non-append evaluated')
    parent = entry((0,0,100,100), None)
    candidates = [entry((0,0,100,50),Never()), entry((0,50,100,100),Never())]
    kw = dict(KW)
    if branch == 'grid_ref':
        kw['grid_ref'] = True
        monkeypatch.setattr(u, '_union_one_to_one_grid_refs', lambda *a,**k: ({0:candidates[0]}, {0,1}))
    elif branch == 'ambiguous':
        monkeypatch.setattr(u, '_union_find_owner', lambda *a: (None, True))
    else:
        monkeypatch.setattr(u, '_union_partition_covers_nodes', lambda *a: True)
    u._union_replace_append_base([parent], candidates, **kw)


def test_provenance_copy_preserves_contract():
    context = c.AppendContext([],[])
    a = entry((0,0,10,10),context)
    a.append_decision = s.Decision('single_record','test',{})
    b = u._entry_with_provenance(a,bbox_operation='union_append')
    assert b.append_context is context and b.append_index == 0
    assert b.append_decision is a.append_decision


def test_formula_does_not_extract_text_or_graphics(monkeypatch):
    chars=[dict(text=t,x0=x,x1=x+5,top=0,bottom=100)
           for t,x in [('(',0),(')',95)]]
    context=c.AppendContext(chars,[])
    i=context.add((10,20,90,40), [[(10,20,50,40),(50,20,90,40)]],False,None)
    monkeypatch.setattr(c,'grid_cell_texts',lambda *a,**k: pytest.fail('text extraction'))
    monkeypatch.setattr(c,'graphic_primitives',lambda *a: pytest.fail('graphics analysis'))
    assert context.decide(i).evidence['external_owner']=='enclosing_math_delimiters'
    assert context._materials is None and not context._texts


def test_char_snapshot_survives_producer_mutation():
    chars=[dict(text='A',x0=1,x1=3,top=1,bottom=3)]
    context=c.AppendContext(chars,[])
    i=context.add((0,0,10,10),[[(0,0,10,10)]],False,True)
    chars[0]['text']='B'; chars.clear()
    assert context.texts(i)[0][1]=='A'


def test_exact_drawing_key_and_scope_no_extraction(monkeypatch):
    doc=u.pymupdf.open();page=doc.new_page()
    monkeypatch.setattr(type(page),'get_drawings',lambda *a,**k:pytest.fail('re-extraction'))
    assert table._cached_table_drawings(page)==()
    with table._html_table_scope():
        cache=table._TABLE_DRAWINGS.get()
        key=table._table_drawings_key(page)
        cache[(page,90,*key[2:])]=['wrong rotation first']
        cache[key]=['correct']
        assert table._cached_table_drawings(page)==['correct']
        with table._html_table_scope():
            assert table._cached_table_drawings(page)==()
        assert table._cached_table_drawings(page)==['correct']
        page.set_rotation(180)
        assert table._cached_table_drawings(page)==()
    assert table._cached_table_drawings(page)==()
    doc.close()


@pytest.mark.parametrize('change', ['cropbox','mediabox','contents'])
def test_other_drawing_state_keys_are_not_interchangeable(change):
    doc=u.pymupdf.open();page=doc.new_page()
    with table._html_table_scope():
        table._TABLE_DRAWINGS.get()[table._table_drawings_key(page)]=['old state']
        if change=='cropbox':page.set_cropbox(u.pymupdf.Rect(0,0,100,100))
        elif change=='mediabox':page.set_mediabox(u.pymupdf.Rect(0,0,700,900))
        else:page.insert_text((20,20),'new content stream')
        assert table._cached_table_drawings(page)==()
    doc.close()


def test_parallel_drawing_scopes_are_isolated():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    barrier=Barrier(2)
    # Test ContextVar lifetime without invoking MuPDF concurrently in threads.
    class PageState:
        rotation=0
        rect=cropbox=mediabox=(0,0,100,100)
        def get_contents(self):return [7]
    def worker(label):
        page=PageState()
        with table._html_table_scope():
            cache=table._TABLE_DRAWINGS.get()
            cache[table._table_drawings_key(page)]=[label]
            barrier.wait(timeout=10)
            value=table._cached_table_drawings(page)
            assert len(cache)==1
        return value
    with ThreadPoolExecutor(2) as pool:
        assert list(pool.map(worker,['first','second']))==[['first'],['second']]




def test_consumed_peer_retained_as_component_evidence(monkeypatch):
    ctx=c.AppendContext([],[])
    for y in (0,20): ctx.add((0,y,20,y+10),[[(0,y,20,y+10)]],True,True)
    def peer_rule(candidates,*a,**k):
        assert len(candidates)==2
        return {1:'peer_proof'}
    monkeypatch.setattr(components,'component_vetoes',peer_rule)
    # Candidate 0 can be consumed by grid_ref; only 1 is evaluated.
    assert ctx.veto(1)=='peer_proof'
    assert 0 not in ctx._verdicts
