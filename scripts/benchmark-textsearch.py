"""Compare exact and fuzzy page search. Run serially on an idle machine.

Usage: python scripts/benchmark-textsearch.py --output benchmark.json
Timings include result construction (quads for both APIs). PDF generation,
opening files and constructing a reused TextPage are outside the timed region.
The reported "hits" count is the API list length: quad fragments for exact
search and grouped occurrences for fuzzy search, so these counts can differ.
"""
import argparse
import gc
import hashlib
import json
import platform
import random
import statistics
import subprocess
import textwrap
import time
import timeit
import tracemalloc
from pathlib import Path

import pymupdf


def measure(call):
    start = time.perf_counter()
    result = call()
    elapsed = time.perf_counter() - start
    count = max(1, min(200, int(0.025 / max(elapsed, 1e-6))))
    samples = [1000 * value / count
               for value in timeit.repeat(call, number=count, repeat=5)]
    return dict(median_ms=statistics.median(samples), min_ms=min(samples),
                max_ms=max(samples), iterations=count, repeats=5, hits=len(result))


def make_page(length, repeated=False):
    rng = random.Random(947)
    text = "a" * length if repeated else " ".join(
        "".join(rng.choices("abcdefghijklmnopqrstuvwxyz", k=rng.randint(3, 9)))
        for _ in range(length // 4 + 1))[:length]
    lines = textwrap.wrap(text, 100)
    doc = pymupdf.open()
    page = doc.new_page(width=650, height=60 + len(lines) * 12)
    page.insert_text((20, 30), "\n".join(lines), fontname="cour", fontsize=8)
    return doc


def query(page, size):
    text = " ".join(page.get_text().split())
    for start in (len(text) // 2, len(text) // 3, 0):
        needle = text[start:start + size].strip()
        if needle and page.search_for(needle):
            return needle
    raise AssertionError("Cannot find an exact benchmark query")


def compare(page, name, size, limit, rows, *, typo=True):
    needle = query(page, size)
    misspelled = list(needle)
    for i in range(limit):
        misspelled[len(needle) // 2 + i] = "#"
    misspelled = "".join(misspelled)
    tp = page.get_textpage(flags=(pymupdf.TEXT_PRESERVE_WHITESPACE
                           | pymupdf.TEXT_PRESERVE_LIGATURES | pymupdf.TEXT_MEDIABOX_CLIP))
    for reuse in (False, True):
        kwargs = dict(textpage=tp) if reuse else {}
        calls = {
            "exact": lambda: page.search_for(needle, quads=True, **kwargs),
            "fuzzy_exact": lambda: page.search_for_fuzzy(needle, max_edits=limit, **kwargs),
        }
        if typo:
            calls["exact_typo"] = lambda: page.search_for(misspelled, quads=True, **kwargs)
            calls["fuzzy_typo"] = lambda: page.search_for_fuzzy(
                misspelled, max_edits=limit, **kwargs)
        row = dict(case=name, page_chars=len(page.get_text()), query_chars=len(needle),
                   max_edits=limit, textpage_reused=reuse)
        for method, call in calls.items():
            row[method] = measure(call)
        assert row["exact"]["hits"] > 0 and row["fuzzy_exact"]["hits"] > 0
        if typo:
            assert row["exact_typo"]["hits"] == 0
            assert row["fuzzy_typo"]["hits"] > 0
        row["slowdown"] = row["fuzzy_exact"]["median_ms"] / row["exact"]["median_ms"]
        rows.append(row)
        print(f'{name}, M={len(needle)}, k={limit}, reuse={reuse}: '
              f'exact={row["exact"]["median_ms"]:.3f}ms '
              f'fuzzy={row["fuzzy_exact"]["median_ms"]:.3f}ms '
              f'({row["slowdown"]:.1f}x)', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    result = dict(environment=dict(python=platform.python_version(),
                  platform=platform.platform(), processor=platform.processor(),
                  pymupdf=pymupdf.__file__, versions=list(pymupdf.version),
                  search_source_sha256=hashlib.sha256(
                      (Path(pymupdf.__file__).parent / "_textsearch.py").read_bytes()).hexdigest(),
                  head=subprocess.check_output(["git", "rev-parse", "HEAD"],
                                               cwd=repo, text=True).strip()),
                  timings=[], python_peak_bytes=[])
    rows = result["timings"]
    for length in (1000, 5000, 20000):
        with make_page(length) as doc:
            for size in (20, 100, 300):
                for limit in (1, 2):
                    compare(doc[0], f"synthetic-{length}", size, limit, rows)
            compare(doc[0], f"zero-budget-{length}", 100, 0, rows, typo=False)
            for method in ("exact", "fuzzy"):
                page = doc[0]
                needle = query(page, 100)
                gc.collect()
                tracemalloc.start()
                if method == "exact":
                    page.search_for(needle, quads=True)
                else:
                    page.search_for_fuzzy(needle, max_edits=2)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                result["python_peak_bytes"].append(dict(chars=length, method=method, peak=peak))
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name in ("2.pdf", "github_sample.pdf"):
        with pymupdf.open(repo / "tests/resources" / name) as doc:
            for size in (20, 100):
                compare(doc[0], name, size, 2, rows)
    with make_page(20000, repeated=True) as doc:
        compare(doc[0], "repeated-20000", 100, 2, rows, typo=False)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
