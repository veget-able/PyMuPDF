"""Build a review wheel using the official draft's unchanged native binaries.

Normal release builds use setup.py with PYMUPDF_SETUP_PATH_4LLM. This helper is
for a reproducible Python-only forward-port check; it does not rebuild MuPDF.
Run from a clean checkout with the matching pymupdf4llm review checkout.
"""
import argparse
import base64
import csv
import hashlib
import io
from pathlib import Path
import subprocess
import zipfile


def tracked(root, path):
    return subprocess.check_output(['git', '-C', str(root), 'ls-files', path], text=True).splitlines()


def build(wheel, llm, output):
    root = Path(__file__).resolve().parents[1]
    expected = 'f92e8a7ae92c7b1cbffcbe8764166ab1234e0a37b07549f5951e7739241d34f0'
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != expected:
        raise ValueError('Expected the pinned Linux x86_64 draft 2.0_c wheel')
    with zipfile.ZipFile(wheel) as source:
        files = {name: source.read(name) for name in source.namelist() if not name.endswith('/')}
    metadata = next(name for name in files if name.endswith('.dist-info/METADATA'))
    assert b'Name: pymupdf\n' in files[metadata] and b'Version: 2.0\n' in files[metadata]
    for package, checkout in [('pymupdf', root), ('pymupdf4llm', llm)]:
        for relative in tracked(checkout, 'src'):
            path = checkout / relative
            name = f'{package}/{Path(relative).relative_to("src").as_posix()}'
            if path.suffix not in ('.py', '.onnx', '.md'):
                continue
            if path.name in ('versions_file.py', '_build.py') or 'build' in Path(relative).parts:
                continue
            if package == 'pymupdf' and name not in files and not path.name.startswith('_table_'):
                continue
            files[name] = path.read_bytes()
    # setup.py declares this new runtime dependency for ordinary builds too.
    if b'Requires-Dist: rapidfuzz' not in files[metadata]:
        header, separator, body = files[metadata].partition(b'\n\n')
        files[metadata] = header + b'\nRequires-Dist: rapidfuzz>=3' + separator + body
    assert 'pymupdf4llm/_table_pipeline/models/fang-header-rf-r6.onnx' in files
    assert not any(b'from parse_bench' in body or b'import parse_bench' in body
                   for name, body in files.items() if name.endswith('.py'))
    record_name = metadata.removesuffix('METADATA') + 'RECORD'
    lines = io.StringIO()
    writer = csv.writer(lines, lineterminator='\n')
    for name, body in sorted(files.items()):
        if name == record_name:
            continue
        digest = base64.urlsafe_b64encode(hashlib.sha256(body).digest()).rstrip(b'=').decode()
        writer.writerow([name, f'sha256={digest}', len(body)])
    writer.writerow([record_name, '', ''])
    files[record_name] = lines.getvalue().encode()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / wheel.name
    if destination.exists():
        raise FileExistsError(destination)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in sorted(files.items()):
            archive.writestr(name, body)
    print(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-wheel', type=Path, required=True)
    parser.add_argument('--pymupdf4llm', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.base_wheel, args.pymupdf4llm.resolve(), args.output)
