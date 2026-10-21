"""Contracts shared by native 2.0 tables and the structured HTML consumer."""
import ast
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pymupdf
from pymupdf import table, _table_pipeline, _table_refine, _table_union
from pymupdf._table_headers import HeaderRegion


def test_no_duplicate_top_level_implementations():
    for module in (table, _table_refine, _table_union):
        nodes = ast.parse(Path(module.__file__).read_text()).body
        names = Counter(n.name for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)))
        assert not {name: count for name, count in names.items() if count > 1}


def test_native_header_is_lazy_and_html_does_not_disable_public_access(monkeypatch):
    calls = []
    header = object()
    monkeypatch.setattr(table.Table, '_get_header', lambda self: calls.append(self) or header)
    with pymupdf.open() as doc:
        page = doc.new_page()
        with table._html_table_scope():
            tab = table.Table(page, [(10, 10, 100, 40)])
            assert not calls
            assert tab.header is header
            assert tab.header is header
        assert calls == [tab]


def test_shared_drawings_are_not_mutated_by_native_consumer(monkeypatch):
    calls = []
    paths = [{'rect': pymupdf.Rect(1, 2, 3, 4),
              'items': [('re', pymupdf.Rect(1, 2, 3, 4), 1)]}]
    monkeypatch.setattr(pymupdf.Page, 'get_drawings', lambda self: calls.append(self) or paths)
    with pymupdf.open() as doc:
        page = doc.new_page()
        page._table_drawings_cache = []
        first = table._get_table_drawings(page, native=True)
        first[0]['rect'].x0 = -100
        assert table._get_table_drawings(page)[0]['rect'].x0 == 1
        assert len(calls) == 1
        with table._html_table_scope():
            shared = table._get_table_drawings(page)
            assert table._cached_table_drawings(page) is shared
            assert table._get_table_drawings(page) is shared
            assert len(calls) == 2


def test_runtime_roles_do_not_run_native_leaf_completion_twice(monkeypatch):
    grid = [[]]
    region = HeaderRegion(0, ())
    calls = []
    monkeypatch.setattr(table, '_refine_placement_or_flat_grid', lambda *a, **k: grid)
    monkeypatch.setattr(table, 'find_header_region', lambda *a: region)
    monkeypatch.setattr(table, 'extend_header_leaf_labels', lambda *a: calls.append('native') or 0)
    runtime = SimpleNamespace(build_roles=lambda page, g, r: (calls.append('r6') or g, r))
    with _table_pipeline.activate(runtime):
        assert table._refine_build_placements(None, [], 0) == (grid, region)
    assert calls == ['r6']
    table._refine_build_placements(None, [], 0)
    assert calls == ['r6', 'native']


def test_repeated_header_call_contract():
    rows = [['A', 'B', 'C'], ['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']] * 2
    assert table._structured_repeated_leading_header_cuts(rows) == (4,)
    assert table._refine_repeated_leading_header_cuts(rows, 1) == (4,)
