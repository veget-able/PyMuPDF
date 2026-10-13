"""Glyph statistics must change cost, not content admission or char ownership."""
import builtins
import random

import pymupdf
import pytest
from pymupdf import _table_union as u


def scalar(chars, rect):
    result = []
    for char in chars:
        if not str(char.get('text') or '').strip():
            continue
        try:
            x = (float(char['x0']) + float(char['x1'])) / 2.0
            y = (float(char['top']) + float(char['bottom'])) / 2.0
            top, bottom = float(char['top']), float(char['bottom'])
        except (KeyError, TypeError, ValueError):
            continue
        if x >= rect.x0 and x < rect.x1 and y >= rect.y0 and y < rect.y1:
            result.append((top, bottom))
    return result


@pytest.fixture(params=[True, False], ids=['numpy', 'no_numpy'])
def backend(request, monkeypatch):
    if request.param:
        pytest.importorskip('numpy')
    else:
        original = builtins.__import__
        def without_numpy(name, *args, **kwargs):
            if name == 'numpy':
                raise ImportError('NumPy deliberately unavailable')
            return original(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', without_numpy)
    return request.param


def test_half_open_empty_invalid_and_order(backend):
    chars = [dict(text='1', x0=x, x1=x, top=y, bottom=y)
             for x in [0, 10, 20] for y in [0, 10, 20]]
    chars += [dict(text=' '), dict(text='x'),
              dict(text='x', x0=None, x1=2, top=1, bottom=2),
              dict(text='x', x0=float('nan'), x1=2, top=1, bottom=2)]
    stats = u._UnionGlyphIntervals(chars)
    assert (stats.array is not None) == backend
    for box in [(0, 0, 10, 10), (10, 10, 20, 20), (0, 0, 0, 0)]:
        rect = pymupdf.Rect(box)
        assert stats.intervals(rect) == scalar(chars, rect)
    assert u._UnionGlyphIntervals([]).intervals(pymupdf.Rect(0, 0, 10, 10)) == []


def test_randomized_cell_selection(backend):
    rng = random.Random(20261013)
    chars = [dict(text=rng.choice(['a', '中', '7', ' ', '']),
                  x0=rng.uniform(-5, 30), x1=rng.uniform(-5, 30),
                  top=rng.uniform(-5, 30), bottom=rng.uniform(-5, 30))
             for _ in range(250)]
    stats = u._UnionGlyphIntervals(chars)
    for _ in range(100):
        x0, x1 = sorted([rng.uniform(-5, 30), rng.uniform(-5, 30)])
        y0, y1 = sorted([rng.uniform(-5, 30), rng.uniform(-5, 30)])
        rect = pymupdf.Rect(x0, y0, x1, y1)
        assert stats.intervals(rect) == scalar(chars, rect)


def test_grid_decisions_match_scalar_membership(backend, monkeypatch):
    rng = random.Random(20261013)
    class ScalarIntervals:
        def intervals(self, rect):
            return scalar(chars, rect)
    for _ in range(100):
        chars = [dict(text=rng.choice(['A', '1', ' ']),
                      x0=rng.uniform(-5, 35), x1=rng.uniform(-5, 35),
                      top=rng.uniform(-5, 35), bottom=rng.uniform(-5, 35))
                 for _ in range(rng.randrange(50))]
        grid = [[None if rng.random() < .2 else
                 (c*10, r*10, (c+1)*10, (r+1)*10)
                 for c in range(rng.randrange(1, 4))]
                for r in range(rng.randrange(4))]
        monkeypatch.setattr(u, 'CHARS', chars)
        assert u._union_grid_has_2d_content_support(grid) == (
            u._union_grid_has_2d_content_support(grid, glyphs=ScalarIntervals()))


def test_direct_calls_do_not_keep_previous_chars(backend, monkeypatch):
    grid = [[(0, 0, 10, 10), (10, 0, 20, 10)]]
    monkeypatch.setattr(u, 'CHARS', [dict(text='x', x0=x, x1=x+1, top=1, bottom=2)
                                    for x in [1, 11]])
    assert u._union_grid_has_2d_content_support(grid)
    monkeypatch.setattr(u, 'CHARS', [])
    assert not u._union_grid_has_2d_content_support(grid)


def test_admission_snapshot_reused_and_call_local(backend, monkeypatch):
    from pymupdf import table
    from types import SimpleNamespace
    original = u._UnionGlyphIntervals
    snapshots = []
    def make(chars):
        result = original(chars)
        snapshots.append(result)
        return result
    groups = [[(0, 0, 10, 10), (10, 0, 20, 10)],
              [(0, 20, 10, 30), (10, 20, 20, 30)]]
    def finder(page, **kwargs):
        kwargs['_cell_group_filter'](page, groups)
        return object()
    monkeypatch.setattr(u, '_UnionGlyphIntervals', make)
    monkeypatch.setattr(table, 'find_tables', finder)
    monkeypatch.setattr(u, '_union_candidate_inside_picture', lambda *a: False)
    monkeypatch.setattr(u, '_union_candidate_conflicts_with_layout', lambda *a: True)
    monkeypatch.setattr(u, 'CHARS', [dict(text='x', x0=x, x1=x+1, top=y, bottom=y+1)
                                    for x in [1, 11] for y in [1, 21]])
    assert len(u._union_line_candidates(SimpleNamespace())[0]) == 2
    assert len(snapshots) == 1
    monkeypatch.setattr(u, 'CHARS', [])
    assert len(u._union_line_candidates(SimpleNamespace())[0]) == 0
    assert len(snapshots) == 2
    groups.clear()
    assert len(u._union_line_candidates(SimpleNamespace())[0]) == 0
    assert len(snapshots) == 2  # No eager preparation when no candidate exists.
