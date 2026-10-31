# OCR correction 7: documentation-only companion

Branch: ocr/writeback-correction/writeback-fonts-20261031

This PyMuPDF branch changes documentation only; executable core/native/dependency files remain byte-identical to frozen main. The implementation is in the paired [pymupdf4llm branch](https://github.com/veget-able/pymupdf4llm/tree/ocr/writeback-correction/writeback-fonts-20261031). Applying this companion alone does not enable the correction. Both review commits directly parent their own repository main and have no correction-feature dependencies.

# OCR correction 7: writeback fonts and mixed-font spacing

Branch: ocr/writeback-correction/writeback-fonts-20261031

Independent direct-main correction. The selector branch and correction features1–6 remain unchanged.

Correct REC Unicode can be lost when the PDF writing font lacks a glyph. This change selects covering built-in fonts, avoids existing PDF font-resource aliases, and keeps adjacent font runs from the same REC string together during Markdown generation.

## Scope

- Writing fonts: existing Droid Sans Fallback, MuPDF built-in Noto Serif Devanagari, Helvetica and ZapfDingbats. No external font download or new recognition model.
- Preserve an existing covering font plan. Otherwise choose supported font runs while keeping combining-character clusters together. This is a finite font pool, not universal Unicode coverage or a general shaping engine.
- Reserve unused PDF font aliases before registration. Existing PDF font resources are retained.
- Mark a mixed write only when the before/after extracted spans identify the newly written runs exactly. The formatter joins only adjacent spans with the same REC owner, continuous character offsets and matching source text. Original spaces, separate REC results and unrelated native spans keep their existing behavior.
- Page selection, stored-text classification, render, Rapid DET/REC, public options and KEEP/DROP rules remain those of the target base. This feature does not require another correction branch or the historical REPAIR implementation.

## Further font additions

Add or expand fonts only when a concrete missing-font or missing-glyph case is confirmed. First compare raw REC Unicode with PDF write/save/reextract and final output; separate an already incorrect REC result from a writing loss. Record the document/character and selected font, add a minimal regression test, then validate the fallback and affected output quality. Do not expand the font pool speculatively.

## Current-main quality evidence

Frozen main: pymupdf4llm 363f177ef50deb05f07db8bf2061e7b9c8102b07 and PyMuPDF 1d34e04da00b7673a0b2c3f68b5a5246793a50b8. These are main-based results, not the older integrated IMF2 ROI/REPAIR score.

- CF: 79.6709087651% -> 79.6832432844%, +0.0123345193 percentage points; 3 improved, 0 regressed.
- SF: 56.6573495337% -> 56.7414138612%, +0.0840643275 percentage points; 1 improved, 0 regressed.
- Same 507 PDFs / 509 pages; CF506, SF476 supported / 456 defined. Official reference scorer 8c63e84eff6e51b943496492651ee27e9e71663f.
- Candidate public extraction ran for all 507 documents. All 509 page-selection tuples and 188 Rapid input RGB hashes match the existing main. Stored 7,023 REC strings were replayed after exact-input validation; new DET/REC inference calls: 0.
- Baseline reproduction freshly ran 9 affected/control documents and matched existing main Markdown. Official workers freshly scored 8 changed-output cases; 974 unchanged full-output/case/scorer/SHA-verified scores were reused.
- Final Markdown changed in 4 documents. The other 503 were identical. Page-level selector accuracy is unaffected; CF/SF are document quality metrics.

## Complete changed-output cases

### text/text_ocr__glitch — Changed output

PDF: docs/text/text_ocr__glitch.pdf; page1. Page selected: True; Rapid calls: 1. All cases here are single-page documents.

- CF: 75.91439074% -> 78.37687949%, +2.46248876 percentage points.
- SF: 13.06818182% -> 13.06818182%, +0.00000000 percentage points.
- Restores Romanian ț/ș lost by the original CJK writing font.

### text/text_ocr__routier — Changed output

PDF: docs/text/text_ocr__routier.pdf; page1. Page selected: True; Rapid calls: 1. All cases here are single-page documents.

- CF: 80.83080229% -> 84.60283190%, +3.77202960 percentage points.
- SF: 0.00000000% -> 38.33333333%, +38.33333333 percentage points.
- Restores Romanian letters. Font/text attributes also change downstream layout, so the SF gain is not attributed solely to character accuracy.

### text/text_ocr__ref — Changed output

PDF: docs/text/text_ocr__ref.pdf; page1. Page selected: True; Rapid calls: 1. All cases here are single-page documents.

- CF: 72.19144496% -> 72.19819338%, +0.00674842 percentage points.
- SF: 50.00000000% -> 50.00000000%, +0.00000000 percentage points.
- Preserves REC output containing ș. Font preservation does not establish that the REC spelling itself is correct.

### text/text_handwritting__math — Changed output

PDF: docs/text/text_handwritting__math.pdf; page1. Page selected: True; Rapid calls: 1. All cases here are single-page documents.

- CF: 36.74169191% -> 36.74169191%, +0.00000000 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.
- Preserves ∆; CF/SF stay unchanged. This is not evidence of page-GT handwriting-policy improvement.

### text/text_simple__iehp — Unchanged comparison case

PDF: docs/text/text_simple__iehp.pdf; page1. Page selected: False; Rapid calls: 0. All cases here are single-page documents.

- CF: 94.04940089% -> 94.04940089%, +0.00000000 percentage points.
- SF: 75.00000000% -> 75.00000000%, +0.00000000 percentage points.
- Main does not select this page for OCR, so no font write is reached. The historical integrated handoff selected it; that older score must not be substituted here.

## Processing cost

Same9 documents,3 repetitions per arm, sequential AB/BA/AB order, CPU12, ORT intra/inter1 and OMP/OpenBLAS/MKL1. Imports and9-document process warmups were measured separately. All timing outputs match the quality-run Markdown. Stored REC replay replaces DET/REC inference, so these are replay-pipeline and writing costs, not actual full OCR inference latency or total507-document time.

- Baseline: 3.3940s per9 documents; mean 377.113ms/document, p95 1826.690ms.
- Candidate: 3.4459s per9 documents; mean 382.881ms/document, p95 1842.483ms.
- Writing-stage delta: +50.296ms per9-document batch, approximately +10.059ms per writing page in the5 writing pages /223 REC strings. This sample is not representative of every document.
- Main replay has zero mixed-font results. Separate synthetic mixed-run measurements showed owner capture adds approximately0.4ms with no native spans and1.8ms with200 native spans per mixed write. It extracts page text before and after the write; cost can grow with page text and mixed-result count.

## Persistence and other limits

- Fonts and Unicode survive PDF save/reopen. REC ownership metadata lives on the current Python Page object and is not serialized into the PDF.
- In the same OCR-to-Markdown session IE❤HP stays IE❤HP. After saving and reopening, raw get_text still returns IE❤HP, while Markdown may become IE ❤ HP. This feature does not promise persistent mixed-run spacing across PDF reopening.
- Some Devanagari-plus-symbol combinations, for example ț漢字प❤, are still rejected by the supplied prior planner before extended fallback. This was not present in the evaluated REC corpus and is not fixed here.
- Unsupported scripts, already wrong recognition, legacy font mappings, visual shaping and other native versions are not established by this evaluation.
- Existing1.28.0 was not rerun; this is a feature comparison on2.0-based main, not a version benchmark.

## Validation and reproduction

- Main-specific22 regression tests cover PDF Unicode roundtrip, resource collisions, source-contiguity boundaries and existing full/detection KEEP/DROP behavior. Historical174 tests belong to the older integrated source and are not claimed as current-main test results.
- From the paired pymupdf4llm checkout, run: python examples/check_ocr_writeback_fonts.py. Use matching PyMuPDF 2.0 main Python bindings (1d34e04 or compatible) and pytest; older draft-c bindings lack the layout API used by this main. The runner copies this checkout's source into a temporary package, generates only its required version metadata, and runs the tests without dependency installation, wheels or installed-package changes.
- Use an existing compatible PyMuPDF2.0 environment. Load this checkout’s src as pymupdf4llm through the same source overlay mechanism used by PyMuPDF2.0 builds; do not accidentally test the installed historical package.
- Run pytest with --noconftest and -p no:cacheprovider when using the repository tests, because its existing conftest performs dependency installation. The validated test is tests/test_ocr_writeback_fonts.py.
- Local full validation evidence: runs/OCR_WRITEBACK_MAIN_VALIDATION_20261031/ under the pb_ocr research workspace; source/REC RGB checks, official scores, timing and reopen reports are retained there.
- [Machine-readable results and complete per-document deltas](docs/ocr-writeback-fonts/results.json).
- This source change does not build or publish wheels, update installed packages, or deploy the viewer.

## IMF2 ROI combination and complete cases

The delivery branch contains only feature7 on main. The following auxiliary evaluation composes the existing selector0 and feature7 in a separate runtime, without inheriting corrections1–6. It is not the older integrated REPAIR score.

- CF: 80.2323814244% -> 80.2447159437%, +0.0123345193 percentage points; improved 3, regressed 0.
- SF: 57.5318031859% -> 57.6158675133%, +0.0840643275 percentage points; improved 1, regressed 0.
- All 507 candidate documents were freshly passed through public selection/render/writeback/GNN/Markdown. All 509 decision tuples and 265 Rapid RGB inputs match selector0; 7546 saved REC strings were replayed. New DET/REC inference calls: 0.
- Fresh official worker scores: 10; unchanged exact-output/case/scorer/SHA score reuses: 972.
- Baseline9 affected/control documents were freshly reproduced and matched the prior selector-only outputs. The P2 timing sample above is not reused as IMF2 timing.

### text/text_handwritting__math

PDF: docs/text/text_handwritting__math.pdf; page1. Selection pages: [1]; Rapid calls: 1; Markdown changed: True.

- CF: 36.74169191% -> 36.74169191%, +0.00000000 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.

### text/text_ocr__glitch

PDF: docs/text/text_ocr__glitch.pdf; page1. Selection pages: [1]; Rapid calls: 1; Markdown changed: True.

- CF: 75.91439074% -> 78.37687949%, +2.46248876 percentage points.
- SF: 13.06818182% -> 13.06818182%, +0.00000000 percentage points.

### text/text_ocr__ref

PDF: docs/text/text_ocr__ref.pdf; page1. Selection pages: [1]; Rapid calls: 1; Markdown changed: True.

- CF: 72.19144496% -> 72.19819338%, +0.00674842 percentage points.
- SF: 50.00000000% -> 50.00000000%, +0.00000000 percentage points.

### text/text_ocr__routier

PDF: docs/text/text_ocr__routier.pdf; page1. Selection pages: [1]; Rapid calls: 1; Markdown changed: True.

- CF: 80.83080229% -> 84.60283190%, +3.77202960 percentage points.
- SF: 0.00000000% -> 38.33333333%, +38.33333333 percentage points.

### text/text_simple__iehp

PDF: docs/text/text_simple__iehp.pdf; page1. Selection pages: [1]; Rapid calls: 1; Markdown changed: True.

- CF: 93.54966189% -> 93.54966189%, +0.00000000 percentage points.
- SF: 75.00000000% -> 75.00000000%, +0.00000000 percentage points.

## Selector comparison on the same font correction

Comparison: 0+7 (IMF2 ROI plus fonts) versus7 (P2+ODM plus fonts). This measures the selector effect with the writing correction fixed. All changed document scores are listed below; score changes are not assertions of OCR correctness.

- CF: 79.6832432844% -> 80.2447159437%, +0.5614726593 percentage points.
- SF: 56.7414138612% -> 57.6158675133%, +0.8744536521 percentage points.

Unique documents with changed defined CF/SF: 54. Full machine-readable comparisons: [model-comparisons.json](docs/ocr-writeback-fonts/model-comparisons.json).

### text/text_dense__leaflet

PDF: docs/text/text_dense__leaflet.pdf; page1 (single-page document).
- CF: 92.85615807% -> 91.88619121%, -0.96996686 percentage points.
- SF: 60.68376068% -> 68.22344322%, +7.53968254 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_dense__underline

PDF: docs/text/text_dense__underline.pdf; page1 (single-page document).
- CF: 42.75298473% -> 47.82677084%, +5.07378611 percentage points.
- SF: no defined score.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_misc__gridofimages

PDF: docs/text/text_misc__gridofimages.pdf; page1 (single-page document).
- CF: 65.95501184% -> 65.33471109%, -0.62030075 percentage points.
- SF: no defined score.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_misc__ikea3

PDF: docs/text/text_misc__ikea3.pdf; page1 (single-page document).
- CF: 77.34984868% -> 76.76501298%, -0.58483570 percentage points.
- SF: 46.51864035% -> 35.00548246%, -11.51315789 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_misc__json

PDF: docs/text/text_misc__json.pdf; page1 (single-page document).
- CF: 89.12415594% -> 88.84273664%, -0.28141930 percentage points.
- SF: 83.33333333% -> 83.33333333%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__2col_fund_summary

PDF: docs/text/text_multicolumns__2col_fund_summary.pdf; page1 (single-page document).
- CF: 99.74446189% -> 99.28571429%, -0.45874760 percentage points.
- SF: 100.00000000% -> 90.00000000%, -10.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__2colrep

PDF: docs/text/text_multicolumns__2colrep.pdf; page1 (single-page document).
- CF: 97.29870685% -> 97.05198880%, -0.24671805 percentage points.
- SF: 36.60714286% -> 36.60714286%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__2x

PDF: docs/text/text_multicolumns__2x.pdf; page1 (single-page document).
- CF: 89.95946062% -> 92.41538477%, +2.45592415 percentage points.
- SF: 98.74213836% -> 61.24213836%, -37.50000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__3col_statment

PDF: docs/text/text_multicolumns__3col_statment.pdf; page1 (single-page document).
- CF: 80.95256302% -> 83.42169882%, +2.46913580 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__3colpres

PDF: docs/text/text_multicolumns__3colpres.pdf; page1 (single-page document).
- CF: 94.67148046% -> 88.47974066%, -6.19173979 percentage points.
- SF: 62.50000000% -> 62.50000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__article

PDF: docs/text/text_multicolumns__article.pdf; page1 (single-page document).
- CF: 90.91220086% -> 90.86973522%, -0.04246564 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__coorp

PDF: docs/text/text_multicolumns__coorp.pdf; page1 (single-page document).
- CF: 87.02560547% -> 96.09416871%, +9.06856324 percentage points.
- SF: 98.78048780% -> 98.78048780%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__dafta

PDF: docs/text/text_multicolumns__dafta.pdf; page1 (single-page document).
- CF: 91.26830401% -> 94.11662407%, +2.84832007 percentage points.
- SF: 50.00000000% -> 50.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__drill

PDF: docs/text/text_multicolumns__drill.pdf; page1 (single-page document).
- CF: 93.02193837% -> 96.51354957%, +3.49161119 percentage points.
- SF: 66.66666667% -> 58.33333333%, -8.33333333 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__energy2

PDF: docs/text/text_multicolumns__energy2.pdf; page1 (single-page document).
- CF: 85.48155079% -> 93.62038219%, +8.13883140 percentage points.
- SF: 99.10714286% -> 86.60714286%, -12.50000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__esd_end

PDF: docs/text/text_multicolumns__esd_end.pdf; page1 (single-page document).
- CF: 84.03747214% -> 83.63346135%, -0.40401079 percentage points.
- SF: 47.91666667% -> 0.00000000%, -47.91666667 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__esg_whitespace

PDF: docs/text/text_multicolumns__esg_whitespace.pdf; page1 (single-page document).
- CF: 97.60569582% -> 97.01778671%, -0.58790911 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__forword2cols

PDF: docs/text/text_multicolumns__forword2cols.pdf; page1 (single-page document).
- CF: 96.92247058% -> 88.49707366%, -8.42539692 percentage points.
- SF: 100.00000000% -> 50.00000000%, -50.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__heirloom

PDF: docs/text/text_multicolumns__heirloom.pdf; page1 (single-page document).
- CF: 38.09523810% -> 49.12577748%, +11.03053939 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__sbi

PDF: docs/text/text_multicolumns__sbi.pdf; page1 (single-page document).
- CF: 95.70287062% -> 95.68605688%, -0.01681374 percentage points.
- SF: 41.66666667% -> 41.66666667%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__tableOfContent8col

PDF: docs/text/text_multicolumns__tableOfContent8col.pdf; page1 (single-page document).
- CF: 62.09233489% -> 60.30254612%, -1.78978877 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__tableinmiddle2cols

PDF: docs/text/text_multicolumns__tableinmiddle2cols.pdf; page1 (single-page document).
- CF: 57.71836107% -> 82.52859940%, +24.81023833 percentage points.
- SF: 0.00000000% -> 11.25000000%, +11.25000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__visa

PDF: docs/text/text_multicolumns__visa.pdf; page1 (single-page document).
- CF: 87.30837866% -> 91.45566592%, +4.14728727 percentage points.
- SF: 0.00000000% -> 83.33333333%, +83.33333333 percentage points.
- Selection pages P2 -> IMF2: [1] -> []; Rapid calls: 1 -> 0; Markdown changed: True.

### text/text_multicolumns__waterfal

PDF: docs/text/text_multicolumns__waterfal.pdf; page1 (single-page document).
- CF: 94.39107115% -> 79.69297106%, -14.69810008 percentage points.
- SF: 68.33333333% -> 68.33333333%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multicolumns__weeds

PDF: docs/text/text_multicolumns__weeds.pdf; page1 (single-page document).
- CF: 99.23526078% -> 99.06447276%, -0.17078801 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__cnnm

PDF: docs/text/text_multilang__cnnm.pdf; page1 (single-page document).
- CF: 57.14285714% -> 65.98639456%, +8.84353741 percentage points.
- SF: 0.00000000% -> 41.66666667%, +41.66666667 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__greek

PDF: docs/text/text_multilang__greek.pdf; page1 (single-page document).
- CF: 87.71754667% -> 95.94548594%, +8.22793927 percentage points.
- SF: 25.00000000% -> 83.33333333%, +58.33333333 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__japanese5

PDF: docs/text/text_multilang__japanese5.pdf; page1 (single-page document).
- CF: 25.20188786% -> 25.19587786%, -0.00601000 percentage points.
- SF: 44.95967742% -> 47.84135150%, +2.88167408 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__kannada

PDF: docs/text/text_multilang__kannada.pdf; page1 (single-page document).
- CF: 30.37000015% -> 30.69631403%, +0.32631387 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__romanian

PDF: docs/text/text_multilang__romanian.pdf; page1 (single-page document).
- CF: 84.55011505% -> 85.41796688%, +0.86785183 percentage points.
- SF: 91.86813187% -> 87.08791209%, -4.78021978 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__spanish

PDF: docs/text/text_multilang__spanish.pdf; page1 (single-page document).
- CF: 82.04440813% -> 81.93447268%, -0.10993545 percentage points.
- SF: 83.47826087% -> 83.47826087%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__spanish2

PDF: docs/text/text_multilang__spanish2.pdf; page1 (single-page document).
- CF: 93.68765114% -> 93.68765114%, +0.00000000 percentage points.
- SF: 25.00000000% -> 37.50000000%, +12.50000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__turkish

PDF: docs/text/text_multilang__turkish.pdf; page1 (single-page document).
- CF: 89.37777087% -> 90.44824034%, +1.07046947 percentage points.
- SF: 0.00000000% -> 41.66666667%, +41.66666667 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_multilang__ukrainian

PDF: docs/text/text_multilang__ukrainian.pdf; page1 (single-page document).
- CF: 93.13781119% -> 92.77566182%, -0.36214938 percentage points.
- SF: 88.02083333% -> 88.02083333%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_ocr__klein

PDF: docs/text/text_ocr__klein.pdf; page1 (single-page document).
- CF: 45.07486665% -> 60.30019054%, +15.22532388 percentage points.
- SF: 0.00000000% -> 0.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_ocr__mag

PDF: docs/text/text_ocr__mag.pdf; page1 (single-page document).
- CF: 0.00000000% -> 73.38052933%, +73.38052933 percentage points.
- SF: 0.00000000% -> 26.31578947%, +26.31578947 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_ocr__scaninfile

PDF: docs/text/text_ocr__scaninfile.pdf; page1 (single-page document).
- CF: 0.00000000% -> 76.17625130%, +76.17625130 percentage points.
- SF: 0.00000000% -> 40.27777778%, +40.27777778 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__4g

PDF: docs/text/text_simple__4g.pdf; page1 (single-page document).
- CF: 96.50698626% -> 97.38746130%, +0.88047504 percentage points.
- SF: 82.37179487% -> 82.37179487%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__adminplan

PDF: docs/text/text_simple__adminplan.pdf; page1 (single-page document).
- CF: 87.07482993% -> 98.63945578%, +11.56462585 percentage points.
- SF: 0.00000000% -> 66.66666667%, +66.66666667 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__att10k

PDF: docs/text/text_simple__att10k.pdf; page1 (single-page document).
- CF: 62.49973258% -> 20.47879261%, -42.02093997 percentage points.
- SF: no defined score.
- Selection pages P2 -> IMF2: [1] -> []; Rapid calls: 1 -> 0; Markdown changed: True.

### text/text_simple__bottens

PDF: docs/text/text_simple__bottens.pdf; page1 (single-page document).
- CF: 99.02572523% -> 98.65749534%, -0.36822989 percentage points.
- SF: 93.30357143% -> 93.30357143%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__delinea

PDF: docs/text/text_simple__delinea.pdf; page1 (single-page document).
- CF: 93.84429803% -> 93.55888283%, -0.28541520 percentage points.
- SF: 50.00000000% -> 50.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__finra

PDF: docs/text/text_simple__finra.pdf; page1 (single-page document).
- CF: 41.91317941% -> 72.29822482%, +30.38504541 percentage points.
- SF: 0.00000000% -> 22.72727273%, +22.72727273 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__green

PDF: docs/text/text_simple__green.pdf; page1 (single-page document).
- CF: 66.53531347% -> 66.23190594%, -0.30340753 percentage points.
- SF: 50.00000000% -> 62.50000000%, +12.50000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__hex

PDF: docs/text/text_simple__hex.pdf; page1 (single-page document).
- CF: 88.26467217% -> 88.06327975%, -0.20139242 percentage points.
- SF: 83.33333333% -> 83.33333333%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__iehp

PDF: docs/text/text_simple__iehp.pdf; page1 (single-page document).
- CF: 94.04940089% -> 93.54966189%, -0.49973900 percentage points.
- SF: 75.00000000% -> 75.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__italicsummary

PDF: docs/text/text_simple__italicsummary.pdf; page1 (single-page document).
- CF: 97.61904762% -> 99.28722342%, +1.66817580 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__landfill

PDF: docs/text/text_simple__landfill.pdf; page1 (single-page document).
- CF: 38.09523810% -> 80.90008780%, +42.80484971 percentage points.
- SF: 0.00000000% -> 32.80204644%, +32.80204644 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__marknotTable

PDF: docs/text/text_simple__marknotTable.pdf; page1 (single-page document).
- CF: 97.70126659% -> 97.25682215%, -0.44444444 percentage points.
- SF: 84.48275862% -> 84.48275862%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__redirect

PDF: docs/text/text_simple__redirect.pdf; page1 (single-page document).
- CF: 96.03174603% -> 94.70359572%, -1.32815031 percentage points.
- SF: 95.45454545% -> 95.45454545%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__references

PDF: docs/text/text_simple__references.pdf; page1 (single-page document).
- CF: 96.43338143% -> 96.09601828%, -0.33736315 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__state

PDF: docs/text/text_simple__state.pdf; page1 (single-page document).
- CF: 87.74837363% -> 92.20779221%, +4.45941858 percentage points.
- SF: 100.00000000% -> 100.00000000%, +0.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_simple__tagblatt

PDF: docs/text/text_simple__tagblatt.pdf; page1 (single-page document).
- CF: 97.48890484% -> 97.54270819%, +0.05380335 percentage points.
- SF: 79.16666667% -> 100.00000000%, +20.83333333 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.

### text/text_sparse__conductivity

PDF: docs/text/text_sparse__conductivity.pdf; page1 (single-page document).
- CF: 60.95238095% -> 77.34487734%, +16.39249639 percentage points.
- SF: 0.00000000% -> 100.00000000%, +100.00000000 percentage points.
- Selection pages P2 -> IMF2: [] -> [1]; Rapid calls: 0 -> 1; Markdown changed: True.


---

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
