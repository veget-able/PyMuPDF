"""The optional consumer is not a PyMuPDF4LLM dependency of PyMuPDF."""
from pathlib import Path
from types import SimpleNamespace

import pytest
import pymupdf
from pymupdf import _table_pipeline, _table_union


def test_no_consumer_uses_native_union(monkeypatch):
    calls = []
    monkeypatch.setattr(_table_union, '_layout_table_grids_base', lambda page: calls.append(page) or [])
    page = object()
    assert _table_union._layout_table_grids(page) == []
    assert calls == [page]


def test_consumer_dispatch_is_scoped():
    marker = object()
    runtime = SimpleNamespace(pipeline=SimpleNamespace(adapter=SimpleNamespace(primaries=lambda page: marker)))
    with _table_pipeline.activate(runtime):
        assert _table_union._layout_table_grids(None) is marker
    assert _table_pipeline.current() is None


def test_finder_dispatch_and_exception_cleanup():
    def fail(*args, **kwargs):
        raise ValueError('fixture')
    with pymupdf.open() as doc:
        page = doc.new_page()
        with pytest.raises(ValueError, match='fixture'):
            with _table_pipeline.activate(SimpleNamespace(find_tables=fail)):
                page.find_tables()
        assert _table_pipeline.current() is None
        assert page.find_tables().tables == []


def test_all_table_modules_are_in_wheel_manifest():
    root = Path(__file__).resolve().parents[1]
    setup = (root / 'setup.py').read_text()
    for source in (root / 'src').glob('_table*.py'):
        assert f'/src/{source.name}' in setup, source.name
