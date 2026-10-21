"""A short path can paint a long perpendicular rule with a wide butt stroke."""
import copy

import pymupdf
from pymupdf import table
import pytest


def drawing():
    return dict(type="s", items=[("l", pymupdf.Point(100, 200),
                                  pymupdf.Point(100.5, 200))],
                rect=pymupdf.Rect(100, 200, 100.5, 200), width=160,
                lineCap=(0, 0, 0), lineJoin=0, dashes="[] 0",
                closePath=False, stroke_opacity=1, color=(0, 0, 0), fill=None)


def edges(path, clip=None):
    with pymupdf.open() as doc:
        page = doc.new_page(width=400, height=400)
        table.EDGES.clear()
        table.CHARS.clear()
        settings = table.TableSettings.resolve(dict(
            vertical_strategy="lines_strict", horizontal_strategy="lines_strict"))
        table.make_edges(page, tset=settings, paths=[path], clip=clip)
        return [dict(e) for e in table.EDGES if e.get("ruling_origin") == "vector"]


@pytest.mark.parametrize("reverse", [False, True])
def test_short_wide_stroke_uses_painted_axis(reverse):
    path = drawing()
    if reverse:
        _, a, b = path["items"][0]
        path["items"] = [("l", b, a)]
    before = copy.deepcopy(path)
    result = edges(path)
    assert path == before
    assert len(result) == 1
    edge = result[0]
    assert edge["orientation"] == "v"
    assert edge["x0"] == 100.25
    assert (edge["top"], edge["bottom"], edge["linewidth"]) == (120, 280, .5)
    assert len(table.filter_edges(result)) == 1


def test_short_wide_stroke_clips_painted_centerline():
    result = edges(drawing(), clip=(90, 150, 110, 240))
    assert len(result) == 1
    assert (result[0]["top"], result[0]["bottom"]) == (150, 240)


@pytest.mark.parametrize("change", [
    {"lineCap": (1, 1, 1)}, {"lineCap": (2, 2, 2)},
    {"dashes": "[3 2] 0"}, {"width": .5}, {"stroke_opacity": 0},
])
def test_unsupported_stroke_preserves_path_direction(change):
    path = drawing()
    path.update(change)
    result = edges(path)
    assert len(result) == 1
    assert result[0]["orientation"] == "h"


def test_vertical_short_path_and_compound_path():
    path = drawing()
    path["items"] = [("l", pymupdf.Point(100, 200), pymupdf.Point(100, 200.5))]
    assert edges(path)[0]["orientation"] == "h"
    path = drawing()
    path["items"].append(("l", pymupdf.Point(100, 300), pymupdf.Point(200, 300)))
    assert all(e["orientation"] == "h" for e in edges(path))
