"""
Copyright (C) 2023 Artifex Software, Inc.

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

Native text-block serialization for table refinement.

Keep image-preserving TextPage construction: images can separate native lines.
Only skip image serialization, using the existing text-block converter.
"""
import pymupdf
from pymupdf import mupdf


def _table_text_blocks(page, *, raw):
    flags = pymupdf.TEXTFLAGS_RAWDICT if raw else pymupdf.TEXTFLAGS_DICT
    textpage = page.get_textpage(flags=flags)
    native = textpage.this
    if not any(block.m_internal.type == mupdf.FZ_STEXT_BLOCK_IMAGE for block in native):
        data = textpage.extractRAWDICT() if raw else textpage.extractDICT()
        return data['blocks']
    bounds = mupdf.FzRect(native.m_internal.mediabox)
    infinite = mupdf.fz_is_infinite_rect(bounds)
    buffer = mupdf.fz_new_buffer(128)
    blocks = []
    for block in native:
        if block.m_internal.type != mupdf.FZ_STEXT_BLOCK_TEXT:
            continue
        if not infinite and mupdf.fz_is_empty_rect(
            mupdf.fz_intersect_rect(bounds, mupdf.FzRect(block.m_internal.bbox))
        ):
            continue
        item = {"type": block.m_internal.type}
        pymupdf.JM_make_text_block(block, item, raw, buffer, bounds)
        blocks.append(item)
    return blocks
