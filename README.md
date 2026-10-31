# ODM page pixels without normal stored text

Branch: ocr/page-selector/odm-no-text

Independent candidate directly on fixed main. P2 is retained: this is a controlled ODM input change, not ODM-only selection and not an IMF2 branch or a correction bundle. The approved integration remains unchanged.

Paired sources: https://github.com/veget-able/PyMuPDF/tree/ocr/page-selector/odm-no-text and https://github.com/veget-able/pymupdf4llm/tree/ocr/page-selector/odm-no-text. Each repository has one final review commit on main. This repository is a documentation-only companion; its executable tree matches main.

## Contract

- Preserve main P2 heuristics, existing OCR-layer gate, use_ocr/force_ocr and explicit KEEP/DROP/FORCE behavior. No unrelated correction or unconditional Unicode priority is enabled.
- The ODM receives22 features, not an image tensor. Only page_sobel_energy/page_sobel_entropy/page_sobel_var/page_white_ratio change. The other18 original text/layout/embedded-image features remain, including num_spans/text_area. Original weights, feature order and0.93 threshold remain.
- Render at the original72DPI in grayscale, then downsample128x128. Exclude main Rapid-normal stored spans: not ocr_text(span) and no U+FFFD. Native glyph culling uses span bboxes; images/vectors remain. This is not white-box painting or a rewrite of the PDF.
- An empty normal exclusion list returns the original page render, preserving damaged glyphs. OCR-like hidden text and U+FFFD spans are not normal exclusion targets. This is an input-render condition, not a new page damage-selection rule or feature5 priority.
- no-text describes the page pixel input, not zeroing the structural text features or deleting all stored PDF text. The shared/native culling implementation can retain glyphs outside approximate span boxes; no new character mapping/filter is introduced.
- Post-selection Rapid DET/REC, normal-glyph OCR rendering, insertion and output remain those of the target base. No ROI restriction or direct REC is added. No new model file, dependency, retraining or language selection.

## Evaluated scopes and scores

Same507PDF509pages/CF506/SF476 supported456defined; official scorer8c63e84; RapidOCR3.10 PPv6small DET/REC150DPI. Nominal72DPI applies only to ODM page features, not the later OCR render. Main parents: PyMuPDF1d34e04da00b7673a0b2c3f68b5a5246793a50b8 and pymupdf4llm363f177ef50deb05f07db8bf2061e7b9c8102b07. Existing1.28.0 was not rerun; this is a draft-2.0 feature comparison.

- main-odm-no-text: baseline CF79.6709088%/SF56.6573495% -> candidate CF79.7167681%/SF56.8591933%; delta+0.0458594/+0.2018438pp.
  PageGT200: TP85,FP3,FN15,TN97; precision96.5909%,recall85.0000%,F190.4255%.
  P2/ODM cohort and page metadata unchanged;18 feature values matched on every one of299 ODM calls. Page pixel values changed on209 pages. Same selected pages use identical downstream Rapid input.

- corrected-odm-no-text: baseline CF81.9120785%/SF57.9868410% -> candidate CF81.9573219%/SF58.1886848%; delta+0.0452433/+0.2018438pp.
  PageGT200: TP85,FP3,FN15,TN97; precision96.5909%,recall85.0000%,F190.4255%.
  P2/ODM cohort and page metadata unchanged;18 feature values matched on every one of342 ODM calls. Page pixel values changed on209 pages. Same selected pages use identical downstream Rapid input.

The first scope is this branch alone on main. The second is an auxiliary composition on approved corrections1,2,3,4,6,7, retaining P2+ODM and replacing only the two input-feature files. It is not an extra feature inherited by this independent branch, and is not installed/pushed as a replacement of the default IMF2 integration.

Validation:6 renderer/feature tests;641 real feature-parity checks;1014 fresh public output runs. Verified recognition replay427, same-run replay1, new actual DET/REC inputs1. Official workers14 new;1118 exact output/case/scorer matches reused.

Observed public-API campaign span sum330.61s; score validation/scoring9.88s. Spans run from first API start to last successful completion, include4workers/tracing/feature audit, recognition reuse and the initial observer retry pause. They are validation cost, not standalone product latency or a speed ranking. The initial observer incorrectly treated identical original/candidate NaNs in3 documents as a difference; equal_nan comparison fixed the observer only and those3 were retried. Other successful outputs were preserved.

Original ODM weights SHA256:f72d8975dfc650d6761f793dad424939e70bb94a27d13de8d3507033c74fa101. Page-input distribution changes without retraining; the measured gain is not a general accuracy guarantee.

## Reproduction

Use an existing compatible draft-2.0 runtime and the paired branch sources. A source overlay must expose this checkout as pymupdf4llm; do not accidentally benchmark the installed historical package. No wheel build/publication or installation was performed.

python examples/check_odm_no_text.py --core-repo /path/to/PyMuPDF
python -m pytest --noconftest -q -p no:cacheprovider tests/test_odm_no_text.py

The repository conftest can install dependencies, so --noconftest is intentional. The frozen local public API protocol, source overlays, recognition/model hashes, exact features and official scores are in runs/OCR_ODM_NO_TEXT_BRANCH_20261031 in the pb_ocr research workspace. Source/PDF content stays unchanged during rendering.

## Complete improvements, regressions and changed outputs

Per-document scores are percentages; deltas are percentage points. Page1 labels are exact for a single-page PDF. Multi-page quality is aggregated and not attributed to one page. OCR activity is separate evidence; CF/SF gains do not by themselves prove every OCR addition is correct. Full machine-readable cases are in docs/ocr-odm-no-text-cases.json.

### main+input change only

- CF: improved9,regressed4,unchanged493.
- SF: improved3,regressed3,unchanged450.

- text/text_dense__underline; PDF page1.
  Input:docs/text/text_dense__underline.pdf.
  CF: 42.7530% -> 47.8268% (+5.0738pp;improved).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_misc__2pages; PDF page1.
  Input:docs/text/text_misc__2pages.pdf.
  CF: 90.1375% -> 90.1309% (-0.0065pp;regressed).
  SF: 72.7941% -> 72.7941% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_misc__ikea3; PDF page1.
  Input:docs/text/text_misc__ikea3.pdf.
  CF: 77.3498% -> 76.7650% (-0.5848pp;regressed).
  SF: 46.5186% -> 35.0055% (-11.5132pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__drill; PDF page1.
  Input:docs/text/text_multicolumns__drill.pdf.
  CF: 93.0219% -> 96.5135% (+3.4916pp;improved).
  SF: 66.6667% -> 58.3333% (-8.3333pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__elpais; PDF page1.
  Input:docs/text/text_multicolumns__elpais.pdf.
  CF: 70.0184% -> 71.8234% (+1.8051pp;improved).
  SF: 14.1807% -> 34.4013% (+20.2206pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_multicolumns__energy2; PDF page1.
  Input:docs/text/text_multicolumns__energy2.pdf.
  CF: 85.4816% -> 93.6204% (+8.1388pp;improved).
  SF: 99.1071% -> 86.6071% (-12.5000pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__visa; PDF page1.
  Input:docs/text/text_multicolumns__visa.pdf.
  CF: 87.3084% -> 91.4557% (+4.1473pp;improved).
  SF: 0.0000% -> 83.3333% (+83.3333pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_multicolumns__zh; PDF page1.
  Input:docs/text/text_multicolumns__zh.pdf.
  CF: 56.9613% -> 56.9824% (+0.0211pp;improved).
  SF: 12.6263% -> 12.6263% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__4g; PDF page1.
  Input:docs/text/text_simple__4g.pdf.
  CF: 96.5070% -> 97.3875% (+0.8805pp;improved).
  SF: 82.3718% -> 82.3718% (+0.0000pp;unchanged).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_simple__delinea; PDF page1.
  Input:docs/text/text_simple__delinea.pdf.
  CF: 93.8443% -> 93.5589% (-0.2854pp;regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp;unchanged).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_simple__norman; PDF page1.
  Input:docs/text/text_simple__norman.pdf.
  CF: 60.1226% -> 59.5854% (-0.5372pp;regressed).
  SF: 64.5833% -> 85.4167% (+20.8333pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__otago; PDF page1.
  Input:docs/text/text_simple__otago.pdf.
  CF: 96.3256% -> 96.9312% (+0.6056pp;improved).
  SF: 80.3030% -> 80.3030% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__wordForwords; PDF page1.
  Input:docs/text/text_simple__wordForwords.pdf.
  CF: 93.7837% -> 94.2387% (+0.4550pp;improved).
  SF: 96.8750% -> 96.8750% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

### approved corrections1,2,3,4,6,7+input change only

- CF: improved9,regressed4,unchanged493.
- SF: improved3,regressed3,unchanged450.

- text/text_dense__underline; PDF page1.
  Input:docs/text/text_dense__underline.pdf.
  CF: 42.7530% -> 47.8268% (+5.0738pp;improved).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_misc__2pages; PDF page1.
  Input:docs/text/text_misc__2pages.pdf.
  CF: 90.1375% -> 90.1309% (-0.0065pp;regressed).
  SF: 72.7941% -> 72.7941% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_misc__ikea3; PDF page1.
  Input:docs/text/text_misc__ikea3.pdf.
  CF: 77.3498% -> 76.7650% (-0.5848pp;regressed).
  SF: 46.5186% -> 35.0055% (-11.5132pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__drill; PDF page1.
  Input:docs/text/text_multicolumns__drill.pdf.
  CF: 93.0219% -> 96.5135% (+3.4916pp;improved).
  SF: 66.6667% -> 58.3333% (-8.3333pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__elpais; PDF page1.
  Input:docs/text/text_multicolumns__elpais.pdf.
  CF: 70.2900% -> 71.7834% (+1.4934pp;improved).
  SF: 14.1807% -> 34.4013% (+20.2206pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_multicolumns__energy2; PDF page1.
  Input:docs/text/text_multicolumns__energy2.pdf.
  CF: 85.4816% -> 93.6204% (+8.1388pp;improved).
  SF: 99.1071% -> 86.6071% (-12.5000pp;regressed).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_multicolumns__visa; PDF page1.
  Input:docs/text/text_multicolumns__visa.pdf.
  CF: 87.3084% -> 91.4557% (+4.1473pp;improved).
  SF: 0.0000% -> 83.3333% (+83.3333pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_multicolumns__zh; PDF page1.
  Input:docs/text/text_multicolumns__zh.pdf.
  CF: 56.9613% -> 56.9824% (+0.0211pp;improved).
  SF: 12.6263% -> 12.6263% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__4g; PDF page1.
  Input:docs/text/text_simple__4g.pdf.
  CF: 96.5070% -> 97.3875% (+0.8805pp;improved).
  SF: 82.3718% -> 82.3718% (+0.0000pp;unchanged).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_simple__delinea; PDF page1.
  Input:docs/text/text_simple__delinea.pdf.
  CF: 93.8443% -> 93.5589% (-0.2854pp;regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp;unchanged).
  Selected:[]->[1];Rapid:[]->[1];Markdown changed:True.

- text/text_simple__norman; PDF page1.
  Input:docs/text/text_simple__norman.pdf.
  CF: 60.1226% -> 59.5854% (-0.5372pp;regressed).
  SF: 64.5833% -> 85.4167% (+20.8333pp;improved).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__otago; PDF page1.
  Input:docs/text/text_simple__otago.pdf.
  CF: 96.3256% -> 96.9312% (+0.6056pp;improved).
  SF: 80.3030% -> 80.3030% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

- text/text_simple__wordForwords; PDF page1.
  Input:docs/text/text_simple__wordForwords.pdf.
  CF: 93.7837% -> 94.2387% (+0.4550pp;improved).
  SF: 96.8750% -> 96.8750% (+0.0000pp;unchanged).
  Selected:[1]->[];Rapid:[1]->[];Markdown changed:True.

## Original repository README

<p align="center">
  <a href="https://pymupdf.io?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=logo&utm_term=website">
    <img loading="lazy" alt="PyMuPDF" src="https://pymupdf.pro/images/py-mupdf-github-icon.png" width="96px" alt="PyMuPDF logo"/>
  </a>
</p>

# PyMuPDF

<p align="center">
 <a href="https://trendshift.io/repositories/11536" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11536" alt="pymupdf%2FPyMuPDF | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![Docs](https://img.shields.io/badge/docs-live-brightgreen)](https://pymupdf.readthedocs.io?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=badges&utm_term=docs)
[![PyPI Version](https://img.shields.io/pypi/v/pymupdf?color=blue&label=PyPI)](https://pypi.org/project/PyMuPDF/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymupdf)](https://pypi.org/project/pymupdf/)
[![License AGPL](https://img.shields.io/github/license/pymupdf/pymupdf)](https://github.com/pymupdf/PyMuPDF/blob/master/COPYING)
[![PyPI Downloads](https://static.pepy.tech/badge/pymupdf/month)](https://pepy.tech/projects/pymupdf)
[![Github Stars](https://img.shields.io/github/stars/pymupdf/PyMuPDF?style=social)](https://github.com/pymupdf/PyMuPDF/stargazers)
[![Discord](https://img.shields.io/discord/770681584617652264?color=6A7EC2&logo=discord&logoColor=ffffff)](https://artifex.com/discord/artifex?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=badges&utm_term=discord)
[![Forum](https://img.shields.io/badge/Forum-ff6600?logo=python&logoColor=ffffff)](https://forum.mupdf.com/c/general/4?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=badges&utm_term=forum)
[![Twitter](https://img.shields.io/twitter/follow/pymupdf)](https://x.com/pymupdf)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-007ec6)](https://huggingface.co/artifex-software)


**The PDF engine behind over 50 million monthly downloads, powering AI pipelines worldwide.**

**PyMuPDF is a high-performance Python library for data extraction, layout analysis, conversion, rendering and manipulation of PDF (and other) documents.** Built on top of MuPDF — a lightweight, fast C engine — PyMuPDF gives you precise, low-level control over documents alongside high-level convenience APIs.

[![Star on GitHub](https://img.shields.io/github/stars/pymupdf/PyMuPDF.svg?style=for-the-badge&label=Star&logo=github)](https://github.com/pymupdf/PyMuPDF/)

---

## Why PyMuPDF?

- **Fast** — powered by [MuPDF](https://mupdf.com?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=body&utm_term=mupdf), a best-in-class C rendering engine
- **Accurate** — pixel-perfect text extraction with font, color, and position metadata
- **Versatile** — read, write, annotate, redact, merge, split, and convert documents
- **LLM-ready** — structured data with JSON & native Markdown output for RAG and AI pipelines
- **Grounded results** — improved, verifiable results, see: [PyMuPDF & Grounding](https://pymupdf.readthedocs.io/en/latest/grounding.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=pymupdf_grounding)

---

## Installation

```bash
pip install --upgrade pymupdf
```

Wheels are available for **Windows**, **macOS**, and **Linux** on Python 3.11–3.15. If no pre-built wheel exists for your platform, pip will compile from source (requires a C/C++ toolchain).

> PyMuPDF uses the ONNX Runtime for certain layout analysis features - ensure your Python environment can support it. For more details see [PyMuPDF Layout & ONNX Runtime](https://pymupdf.readthedocs.io/en/latest/rag.html#pymupdf-layout-and-onnx-runtime?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=installation)


## PyMuPDF Config

After installation, run the `pymupdf-config` command,
This will review what is installed and show information about what other packages
(Python and otherwise) may be available for your system and could improve accuracy and speed.



### Optional extras

| Package | Purpose |
|---|---|
| `pymupdf-office` | Adds Office document support |
| `pymupdf-fonts` | Extended font collection for text output |
| `rapidocr` | OCR engine ([recommended](#ocr-support)) |
| `tesseract-ocr` | OCR engine|

```bash
# Office support
pip install pymupdf-office

# More fonts
pip install pymupdf-fonts

# OCR
pip install rapidocr

# OCR (Tesseract must be installed separately)
# macOS
brew install tesseract

# Ubuntu / Debian
sudo apt install tesseract-ocr
```

---

## OCR Support

We compared both OCR engines on the [ExtractBench](https://www.extractbench.ai/) document corpus:

| Document length | PDFs  |   PyMuPDF + Tesseract | PyMuPDF + RapidOCR |
|---|---|---|---|
|Short, 1–10 pages  |  252 | 80.39% |  **88.94%** |  
|Medium, 11–50 pages | 98 |  82.72% | **87.00%**  | 
|Long, over 50 pages | 20 |  **30.49%** | 29.22%  | 
|Overall |  370 | 78.31% |  **85.20%** | 


Overall, for the best OCR accuracy, it is recommended to use **RapidOCR**.


## Supported File Formats

### Input

| Category | Formats |
|---|---|
| PDF & derivatives | PDF, XPS, EPUB, CBZ, MOBI, FB2, SVG, TXT, MD |
| Images | PNG, JPEG, BMP, TIFF, GIF, and more |
| PyMuPDF Office | DOC, DOCX, XLS, XLSX, PPT, PPTX, HWP, HWPX |

### Output

| Format | Notes |
|---|---|
| PDF | Full fidelity conversion from Office formats |
| SVG | Vector page rendering |
| Image (PNG, JPEG, …) | Page rasterisation at any DPI |
| Markdown | Structure-aware, LLM-ready |
| JSON | Bounding boxes, layout data, per-element detail |
| Plain text | Fast, lightweight extraction |

---


## Quick start

### Extract text

```python
import pymupdf

doc = pymupdf.open("document.pdf")
for page in doc:
    print(page.get_text())
```

### Extract text with layout metadata

```python
import pymupdf

doc = pymupdf.open("document.pdf")
page = doc[0]

blocks = page.get_text("dict")["blocks"]
for block in blocks:
    if block["type"] == 0:  # text block
        for line in block["lines"]:
            for span in line["spans"]:
                print(f"{span['text']!r}  font={span['font']}  size={span['size']:.1f}")
```

### Extract tables

```python
import pymupdf

doc = pymupdf.open("spreadsheet.pdf")
page = doc[0]

tables = page.find_tables()
for table in tables:
    print(table.to_markdown())

    # or get as Pandas DataFrame
    df = table.to_pandas()
```

### Render a page to an image

```python
import pymupdf

doc = pymupdf.open("document.pdf")
page = doc[0]

pixmap = page.get_pixmap(dpi=150)
pixmap.save("page_0.png")
```

### OCR a scanned document

```python
import pymupdf

doc = pymupdf.open("scanned.pdf")
page = doc[0]

# Requires Tesseract installed and on PATH
text = page.get_textpage_ocr(language="eng").extractText()
print(text)
```

### Convert Markdown to PDF

```python
import pymupdf

md_doc = pymupdf.open("example.md")
md_doc.save("example.pdf")
```

### Convert to Markdown for LLMs

```python
import pymupdf

doc = pymupdf.open("report.pdf")
md = doc.to_markdown()
# Pass directly to your LLM or vector store
print(md)
```

### Annotate and redact

```python
import pymupdf

doc = pymupdf.open("contract.pdf")
page = doc[0]

# Add a highlight annotation
rect = pymupdf.Rect(72, 100, 400, 120)
page.add_highlight_annot(rect)

# Add a redaction and apply it
page.add_redact_annot(rect)
page.apply_redactions()

doc.save("contract_redacted.pdf")
```

### Merge PDFs

```python
import pymupdf

merger = pymupdf.open()
for path in ["part1.pdf", "part2.pdf", "part3.pdf"]:
    merger.insert_pdf(pymupdf.open(path))

merger.save("merged.pdf")
```

### Convert an Office document to PDF

```python
import pymupdf.office

pymupdf.office.unlock("YOUR-LICENSE-KEY")

doc = pymupdf.open("presentation.pptx")
pdf_bytes = doc.convert_to_pdf()

with open("output.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Extract LLM-ready Markdown from a Word document

```python
import pymupdf.office

pymupdf.office.unlock("YOUR-LICENSE-KEY")

pymupdf.office.to_markdown("input.docx", "output.md")
```

---

## Features

### Core capabilities

| Feature | Description |
|---|---|
| **Text extraction** | Plain text, rich dict (font, size, color, bbox), HTML, XML, raw blocks |
| **Table detection** | `find_tables()` — locate, extract, and export tables as Markdown or structured data |
| **Image extraction** | Extract embedded images and render any page to a high-resolution `Pixmap` |
| **Rendering** | Render PDF pages to images or `Pixmap` data for use in UI or other workflows |
| **OCR** | Tesseract integration — full-page or partial OCR, configurable language |
| **Annotations** | Read and write highlights, underlines, squiggly lines, sticky notes, free text, ink, stamps |
| **Redaction** | Add and permanently apply redaction annotations |
| **Forms** | Read and fill PDF AcroForm fields |
| **PDF creation** | Create PDFs directly with the API or quickly convert from Markdown files |
| **PDF editing** | Insert, delete, and reorder pages; set metadata; merge and split documents |
| **Drawing** | Draw lines, curves, rectangles, and circles; insert HTML boxes |
| **Encryption** | Open password-protected PDFs; save with RC4 or AES encryption |
| **Links** | Extract hyperlinks, internal cross-references, and URI targets |
| **Bookmarks** | Read and write the outline / table of contents tree |
| **Metadata** | Title, author, creation date, producer, subject, and custom entries |
| **Color spaces** | RGB, CMYK, greyscale; color space conversion |

### LLM & AI output

`doc = pymupdf.open("document.pdf")` , then:

| Output | API |
|---|---|
| Markdown | `doc.to_markdown(path)` |
| JSON | `doc.to_json(path)` |
| Plain text | `doc.to_text(path)` |

Supports multi-column layouts, natural reading order and page chunking.

---

## Supported Python versions

Python **3.11 – 3.15** (as of v2.0). Wheels ship for:

- `manylinux` x86\_64 and aarch64
- `musllinux` x86\_64
- macOS x86\_64 and arm64
- Windows x86 and x86\_64

---

## Performance

PyMuPDF is built on MuPDF — one of the fastest PDF rendering engines available. Typical benchmarks against pure-Python PDF libraries show **10–50× speed improvements** for text extraction and **100× or more** for page rendering, with a minimal memory footprint.

PyMuPDF processes documents **without a GPU**, cutting infrastructure costs significantly compared to vision-based LLM approaches.

---

## Recipes

<details>
<summary>Extract all images from a PDF</summary>

```python
import pymupdf
from pathlib import Path

doc = pymupdf.open("document.pdf")
out = Path("images")
out.mkdir(exist_ok=True)

for page_index, page in enumerate(doc):
    for img_index, img in enumerate(page.get_images()):
        xref = img[0]
        pix = pymupdf.Pixmap(doc, xref)
        if pix.n > 4:  # convert CMYK
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        pix.save(out / f"page{page_index}_img{img_index}.png")
```
</details>

<details>
<summary>Search for text across a document</summary>

```python
import pymupdf

doc = pymupdf.open("document.pdf")
needle = "confidential"

for page in doc:
    hits = page.search_for(needle)
    if hits:
        print(f"Page {page.number}: {len(hits)} occurrence(s)")
        for rect in hits:
            page.add_highlight_annot(rect)

doc.save("highlighted.pdf")
```
</details>

<details>
<summary>Split a PDF into individual pages</summary>

```python
import pymupdf

doc = pymupdf.open("document.pdf")
for i, page in enumerate(doc):
    out = pymupdf.open()
    out.insert_pdf(doc, from_page=i, to_page=i)
    out.save(f"page_{i + 1}.pdf")
```
</details>

<details>
<summary>Insert a watermark on every page</summary>

```python
import pymupdf

doc = pymupdf.open("document.pdf")
for page in doc:
    page.insert_text(
        point=pymupdf.Point(72, page.rect.height / 2),
        text="DRAFT",
        fontsize=72,
        color=(0.8, 0.8, 0.8),
        rotate=45,
    )

doc.save("watermarked.pdf")
```
</details>

---

## Office Document Processing

PyMuPDF can be extended with PyMuPDF Office. This adds a conversion layer that handles Microsoft and Korean Office formats natively — no Office installation, no COM interop, no LibreOffice subprocess.

Once unlocked, `pymupdf.open()` accepts Office files exactly like PDFs:

```python
import pymupdf.office
pymupdf.office.unlock("YOUR-LICENSE-KEY")

# Works identically regardless of format
for fmt in ["contract.docx", "data.xlsx", "deck.pptx", "report.hwpx"]:
    doc = pymupdf.open(fmt)
    for page in doc:
        print(page.get_text())
```

[Get a trial license key for PyMuPDF Office](https://pymupdf.io/office/try?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=body&utm_term=pymupdf_office) 

**What you can do with Office documents:**

- Extract text and images page-by-page
- Convert to PDF with `doc.convert_to_pdf()`
- Rasterise pages to PNG/JPEG for visual inspection



### Restrictions Without a License Key

When `pymupdf.office.unlock()` is called **without** a key, the following restrictions apply:

| Restriction | Detail |
|---|---|
| Page limit | Only the **first 3 pages** of any document are accessible |
| Time limit | Evaluation period — functionality expires after a set duration |

All other features work normally within these constraints, making it straightforward to prototype before purchasing a license.


---



## Frequently Asked Questions

### Can I use PyMuPDF and PyMuPDF Office without sending data to the cloud?

Yes, absolutely — and this is one of PyMuPDF's most significant advantages.

PyMuPDF runs entirely locally. It is a native Python library built on top of the MuPDF C engine. When you call `pymupdf.open()`, `page.get_text()`, `page.find_tables()`, or any other method, everything executes in-process on your own machine. No data is transmitted anywhere.


There are no telemetry calls, no licence validation callbacks, no cloud dependencies of any kind in the open-source AGPL build or the commercial build. Once the package is installed, it works fully air-gapped.

This makes PyMuPDF well-suited for:

- Regulated industries — healthcare (HIPAA), finance, legal, government, where documents cannot leave a controlled environment
- On-premise deployments — servers with no outbound internet access
- Air-gapped systems — classified or sensitive environments
- Self-hosted RAG pipelines — processing confidential documents locally before feeding an on-premise LLM
- Saving on token costs for document pre-processing before sending data to your LLM

The only thing you need an internet connection for is the initial `pip install`. After that, the package and all its capabilities are entirely self-contained.


### Should I `import pymupdf` or `import fitz`?

Use `import pymupdf`. The `fitz` name is a legacy alias that still works as of v1.24.0+, but `import pymupdf` is the recommended and future-proof approach. The two are interchangeable in existing code:

```python
import pymupdf          # recommended
# import fitz           # legacy alias — still works but avoid for new code
```

### Does PyMuPDF work with Korean, Japanese, or Chinese documents?

Yes — PyMuPDF has solid CJK support

### How do I extract Markdown from PDF for LLM?


This is the best starting point for feeding an LLM or building a RAG pipeline.

```python
import pymupdf

doc = pymupdf.open("report.pdf")
md = doc.to_markdown()
print(md)
# Tables appear as Markdown | col1 | col2 | ... inline with the text
```


### Text extraction returns garbled characters or empty output. Why?

This usually means the PDF uses custom font encodings without a proper character map (CMAP). The font's glyphs are present but cannot be mapped back to Unicode. In these cases:

- Use OCR as a fallback (`page.get_textpage_ocr()`)
- Consider that scanned PDFs will always need OCR — text extraction on scans returns nothing



### How do I extract text from a specific area of a page?

Pass a `clip` rectangle to `get_text()`:

```python
import pymupdf

doc = pymupdf.open("input.pdf")
page = doc[0]

# Define the area you want (x0, y0, x1, y1) in points
clip = pymupdf.Rect(50, 100, 400, 300)
text = page.get_text("text", clip=clip)
```



### How do I search for text and find its location on the page?

```python
import pymupdf

doc = pymupdf.open("input.pdf")
page = doc[0]

# Returns a list of Rect objects surrounding each match
locations = page.search_for("invoice number")
for rect in locations:
    print(rect)  # e.g. Rect(72.0, 120.5, 210.0, 134.0)
```



### `get_images` shows no images but I can clearly see charts in the PDF. Why?

Charts and diagrams created by tools like matplotlib, Excel, or R are typically rendered as vector graphics (PDF drawing commands), not raster images. `get_images` only lists embedded raster image objects and will not detect vector graphics. To capture these, rasterise the entire page with `page.get_pixmap()`.



### How does OCR work in PyMuPDF? Does it require a separate Tesseract installation?

PyMuPDF uses MuPDF's built-in Tesseract-based OCR support, so there is no Python-level `pytesseract` dependency. However, PyMuPDF still needs access to the **Tesseract language data files** (`tessdata`), and automatic tessdata discovery may invoke the `tesseract` executable (for example, to list available languages) if you do not explicitly provide a tessdata path. In practice, the recommended setup is to either install Tesseract so discovery works automatically, or configure the tessdata location yourself via the `tessdata` parameter or the `TESSDATA_PREFIX` environment variable. Over 100 languages are supported.

PyMuPDF also supports RapidOCR - which is the recommended OCR engine - RapidOCR is a pip-installable Python package that runs ONNX models, so it doesn't need a separate Tesseract install or `TESSDATA_PREFIX`.


```python
import pymupdf

doc = pymupdf.open("scanned.pdf")
page = doc[0]

# Get a text page using OCR
tp = page.get_textpage_ocr(language="eng")
text = page.get_text(textpage=tp)
print(text)
```


### How do I run OCR on a standalone image file (not a PDF)?

```python
import pymupdf

pix = pymupdf.Pixmap("image.png")
if pix.alpha:
    pix = pymupdf.Pixmap(pix, 0)  # remove alpha channel — required for OCR

# Wrap in a 1-page PDF and OCR it
doc = pymupdf.open()
page = doc.new_page(width=pix.width, height=pix.height)
page.insert_image(page.rect, pixmap=pix)
tp = page.get_textpage_ocr()
text = page.get_text(textpage=tp)
```


### How do I highlight text in a PDF?

```python
import pymupdf

doc = pymupdf.open("input.pdf")
page = doc[0]

# Use quads=True for accurate highlights on non-horizontal text
quads = page.search_for("important term", quads=True)
page.add_highlight_annot(quads)

doc.save("highlighted.pdf")
```

PyMuPDF supports all standard PDF text markers: highlight, underline, strikeout, and squiggly.



### How do I permanently redact (remove) content from a PDF?

Redaction is a deliberate two-step process so you can review before committing:

```python
import pymupdf

doc = pymupdf.open("input.pdf")
page = doc[0]

# Step 1: Mark the area(s) to redact
rect = page.search_for("confidential")[0]
page.add_redact_annot(rect, fill=(1, 1, 1))  # white fill

# Step 2: Apply — permanently removes the underlying content
page.apply_redactions()

doc.save("redacted.pdf")
```

After `apply_redactions()`, the original content is gone. It cannot be recovered from the saved file.





### How do I read form field values from a PDF?

```python
import pymupdf

doc = pymupdf.open("form.pdf")
page = doc[0]

for field in page.widgets():
    print(f"{field.field_name}: {field.field_value}")
```



### How do I fill in a PDF form programmatically?

```python
import pymupdf

doc = pymupdf.open("form.pdf")
page = doc[0]

for field in page.widgets():
    if field.field_name == "First Name":
        field.field_value = "Ada"
        field.update()

doc.save("filled_form.pdf")
```



### Can I use multithreading with PyMuPDF?

No. PyMuPDF does not support multithreaded use, even with Python's newer free-threading mode. The underlying MuPDF library only provides partial thread safety, and a fully thread-safe PyMuPDF implementation would still impose a single-threaded overhead — negating the benefit.

**Use multiprocessing instead.** Each process opens the file independently and works on its own page range:

```python
from multiprocessing import Pool
import pymupdf

def process_pages(args):
    path, start, end = args
    doc = pymupdf.open(path)  # each process opens its own handle
    results = []
    for i in range(start, end):
        results.append(doc[i].get_text())
    return results

with Pool(4) as pool:
    chunks = [("input.pdf", 0, 25), ("input.pdf", 25, 50), ...]
    all_results = pool.map(process_pages, chunks)
```



### How can I speed up repeated text extraction on the same page?

Reuse a `TextPage` object. Creating a `TextPage` is the expensive part — once created, switching between extraction formats is cheap:

```python
import pymupdf

page = doc[0]
tp = page.get_textpage()  # create once

text  = page.get_text("text",    textpage=tp)
words = page.get_text("words",   textpage=tp)
data  = page.get_text("dict",    textpage=tp)
```

This can reduce execution time by 50–95% for repeated extractions on the same page.




### How do I read and write PDF metadata?

```python
import pymupdf

doc = pymupdf.open("input.pdf")

# Read
print(doc.metadata)
# {'title': '...', 'author': '...', 'subject': '...', 'keywords': '...', ...}

# Write
doc.set_metadata({
    "title": "Annual Report 2025",
    "author": "Finance Team",
    "keywords": "annual, finance, 2025"
})
doc.save("output.pdf")
```


### How do I read or set the table of contents / bookmarks?

```python
import pymupdf

doc = pymupdf.open("input.pdf")

# Read — returns a list of [level, title, page_number] entries
toc = doc.get_toc()
for level, title, page in toc:
    print(" " * level, title, "→ page", page)

# Write
new_toc = [
    [1, "Introduction",  1],
    [1, "Methods",       5],
    [2, "Data sources",  6],
]
doc.set_toc(new_toc)
doc.save("output.pdf")
```



---

## Documentation

Full installation guide, API reference, cookbook, and tutorial at **[pymupdf.readthedocs.io](https://pymupdf.readthedocs.io?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=docs)**.

- [Installation guide](https://pymupdf.readthedocs.io/en/latest/installation.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=installation)
- [API reference](https://pymupdf.readthedocs.io/en/latest/classes.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=classes)
- [Cookbook](https://pymupdf.readthedocs.io/en/latest/the-basics.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=the_basics)
- [Tutorial](https://pymupdf.readthedocs.io/en/latest/tutorial.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=tutorial)
- [Changelog](https://pymupdf.readthedocs.io/en/latest/changes.html?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=changelog)
- [PyMuPDF Office docs](https://pymupdf.readthedocs.io/en/latest/pymupdf-office?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=documentation_community&utm_term=pymupdf_office)



---

## Licensing

PyMuPDF and MuPDF are maintained by [Artifex Software, Inc.](https://artifex.com?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=footer&utm_term=website)

- **Open source** — [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html). Free for open-source projects.
- **Commercial** — separate commercial licences available from [Artifex](https://artifex.com/licensing?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=footer&utm_term=licensing) for proprietary applications.

---

## Contributing

Contributions are welcome. Please open an issue before submitting large pull requests.

- [Issue tracker](https://github.com/pymupdf/PyMuPDF/issues)
- [Discord community](https://artifex.com/discord/artifex?utm_source=github&utm_medium=referral&utm_campaign=pymupdf_github&utm_content=footer&utm_term=discord)

## ⭐ Support this project

If you find this useful, please consider giving it a star — it helps others discover it!

[![Star on GitHub](https://img.shields.io/github/stars/pymupdf/PyMuPDF.svg?style=for-the-badge&label=Star&logo=github)](https://github.com/pymupdf/PyMuPDF/)
