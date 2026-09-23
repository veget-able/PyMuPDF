"""Private, call-scoped integration points for structured table consumers.

PyMuPDF has no dependency on PyMuPDF4LLM. With no consumer active, all public
layout/finder calls retain their original behavior. Consumers supply the
existing layout material and refinement decisions; this module performs no
inference and owns no document objects after the scope exits.
"""
from contextlib import contextmanager
from contextvars import ContextVar

_ACTIVE = ContextVar("pymupdf_table_pipeline", default=None)


def current():
    return _ACTIVE.get()


@contextmanager
def activate(runtime):
    if current() is not None:
        raise RuntimeError("Nested structured table pipelines are not supported")
    token = _ACTIVE.set(runtime)
    try:
        yield runtime
    finally:
        _ACTIVE.reset(token)
