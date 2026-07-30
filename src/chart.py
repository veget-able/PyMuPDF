"""
Copyright (C) 2026 Artifex Software, Inc.

This file is part of PyMuPDF.

PyMuPDF is free software: you can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

PyMuPDF is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with MuPDF. If not, see <https://www.gnu.org/licenses/agpl-3.0.en.html>

Alternative licensing terms are available from the licensor.
For commercial licensing, see <https://www.artifex.com/> or contact
Artifex Software, Inc., 39 Mesa Street, Suite 108A, San Francisco,
CA 94129, USA, for further information.

---------------------------------------------------------------------

Chart detection for PDF pages.

Implements Page.find_charts(), a thin page-level API around the chart
detection model shipped with the optional pymupdf_layout package. It
mirrors the division of labor used for table recognition: the detection
model and its ONNX runtime live in pymupdf.layout, while this module
only invokes the detector and converts the raw results to Rect-based
Chart(rect, score) tuples. If the page is rotated, coordinates refer to
the derotated page - consistent with the behavior of Page.find_tables().
"""

import collections

import pymupdf

Chart = collections.namedtuple("Chart", ["rect", "score"])


def find_charts(
    page,
    threshold=0.5,
    providers=None,
    device_id=0,
    model_path=None,
):
    """Detect chart regions on the page.

    Requires the optional pymupdf_layout package which ships the chart
    detection model ('pip install pymupdf-layout').

    Args:
        page: the Page to analyze.
        threshold: minimum detection confidence, a float in [0, 1].
        providers: optional ONNX runtime provider selection, e.g. "cuda".
            Default uses the CPU.
        device_id: GPU ordinal, only relevant with "cuda".
        model_path: optional path of an alternative detection model.

    Returns:
        A list of Chart(rect, score) items in no particular order.
    """
    try:
        from pymupdf.layout import chart_finder
    except ImportError:
        raise RuntimeError(
            "Page.find_charts() needs the optional 'pymupdf_layout'"
            " package - install it via 'pip install pymupdf-layout'."
        ) from None
    raw = chart_finder.find_charts(
        page,
        threshold=threshold,
        providers=providers,
        device_id=device_id,
        model_path=model_path,
    )
    return [Chart(pymupdf.Rect(item["bbox"]), item["score"]) for item in raw]
