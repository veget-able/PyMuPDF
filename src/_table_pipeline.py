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


def retain_span_material(page,blocks):
    """Pass already-produced span material to the current runtime consumer."""
    runtime=current()
    if runtime is not None:
        runtime.accept_source_spans(page,blocks)
    return blocks


def retain_raster_material(page, image, *, scale=1., space='RGB'):
    """Retain an existing producer raster, without changing its array."""
    runtime=current()
    if runtime is not None:
        runtime.accept_raster_material(page,image,scale=scale,space=space)
    return image


def cached_raster_material(page, *, scale=1., space='RGB'):
    runtime=current()
    if runtime is None:return None
    return runtime.cached_raster_material(page,scale=scale,space=space)
