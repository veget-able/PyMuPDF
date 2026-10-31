# Approved OCR integration: feature5 excluded

Branch: ocr/integration/all-features-20261031

Current active features:0,1,2,3,4,6,7. Feature5 Unicode damage recovery is excluded by explicit user decision. The independent feature5 branch is preserved for standalone review; it is not merged into this integration. The branch name remains stable.

Use the same branch in both repositories: https://github.com/veget-able/PyMuPDF/tree/ocr/integration/all-features-20261031 and https://github.com/veget-able/pymupdf4llm/tree/ocr/integration/all-features-20261031. Each is one final review commit directly on frozen main.

## Included branches

- 0: IMF2 ROI page selector.
  PyMuPDF: ocr/page-selector/imf2-roi-selector-20261027; source 5841ec7b94300e6b2442a19e901912b0bc6b9cba.
  pymupdf4llm: ocr/page-selector/imf2-roi-selector-20261027; source 508fe23fb37a081a868f819a0aa0418065b6d5ae.
- 1: Rotated text output.
  PyMuPDF: ocr/output-correction/rotated-text-20261030; source 1983f03d1fd422382523b542a2d741bf86ff6d96.
  pymupdf4llm: ocr/output-correction/rotated-text-20261030; source 9a96c303d6299bf1cb8a69db663e6a6f54ab69b2.
- 2: CropBox rotation correction.
  PyMuPDF: ocr/input-correction/cropbox-rotation-20261030; source d5dd452588f7004bae4324d1b9bedfb895ad23bd.
  pymupdf4llm: ocr/input-correction/cropbox-rotation-20261030; source 8e101462e424b19b9724195bb13428a949eb305c.
- 3: Verified Form BBox input preparation.
  PyMuPDF: ocr/input-correction/form-bbox-input-20261030; source 0f64bf02a7e3bdeef87413079edda927f5278e7e.
  pymupdf4llm: ocr/input-correction/form-bbox-input-20261030; source 96c7856975ec84f458e32c8ba6c42d6edc32fe3e.
- 4: Default True existing-OCR gate bypass.
  PyMuPDF: ocr/selection-policy/existing-ocr-gate-bypass-20261030; source 445ce9d25ae4a388c5dee50b58229b38080b5e57.
  pymupdf4llm: ocr/selection-policy/existing-ocr-gate-bypass-20261030; source 6094a091c009cc87aa2c2e53f18e132c548dea89.
- 6: Symbol damage selection/render/mapped replacement.
  PyMuPDF: ocr/stored-text-recovery/symbol-damage-recovery-20261030; source df8367743cc6d578fed0bd51c3f8cf2ad4c14fde.
  pymupdf4llm: ocr/stored-text-recovery/symbol-damage-recovery-20261030; source db33fccf0c1fc32b6d2735dff52cde2de9cbd299.
- 7: Writeback fonts and same-result mixed-font spacing.
  pymupdf4llm: ocr/writeback-correction/writeback-fonts-20261031; source e91486977eca9c35436f4c44575ae0186fc3c4af.
  PyMuPDF: ocr/writeback-correction/writeback-fonts-20261031; source fd5f686c8032b8c6d9f598134f169238d439d8d8.

## Excluded branch5 and investigation

Do not merge ocr/stored-text-recovery/unicode-damage-recovery-20261030 into the current profile. This exclusion removes its unconditional U+FFFD priority and activated special render fallback. The sources were recomposed from the remaining independent branches, including their original callbacks; the unicode_priority module and standalone feature5 tests are absent.

Main generic U+FFFD handling and feature6 passive Unicode inventory/marker-aware targets remain. Feature6 can still select dense U+FFFD under its distinct symbol criterion; that is not the excluded one-marker priority. Source-shared helper code never enables the missing priority module.

The independent feature5 README documented CF+0.2972pp on selector0 alone, with improvements in eller/att10k/grayson and a Hindi regression. In the historical full0-7 profile the first three remain recovered without5 through feature6; feature4 also recovers eller/grayson. Their Rapid input and Markdown are identical with/without5. Of23 Unicode-selected pages,9 fallback to symbol priority and12 to IMF2 ROI. paper2 has no REC output. Hindi is the only changed-quality case: CF34.0984% without5 versus33.1693% with5; its28 REC strings contain no Devanagari characters. The regression predates integration. The independent Unicode/renderer source files matched byte-for-byte; no omitted feature5 merge was found.

The old full0-7 CF82.6694292%/SF58.7090060% and its conditional feature contributions are historical evidence, not current profile scores. Their artifacts remain in OCR_ALL_FEATURES_INTEGRATION_20261031 and OCR_INTEGRATED_FEATURE_CONTRIBUTIONS_20261031. Current exclusion decision/audit: OCR_UNICODE_README_MERGE_AUDIT_20261031 and OCR_INTEGRATION_EXCLUDE_UNICODE_20261031.

## Policy and input contract

- Default use_ocr=True enables feature4 and symbol feature6. Explicit KEEP/DROP/FORCE and OFF/None retain inherited contracts. TODO: REPAIR naming/API remains deferred; no new REPAIR enum or to_markdown policy parameter is introduced.
- IMF2 ROI only returns page selection. It never crops or filters common Rapid DET/REC. Common normal-glyph culling and full-page OCR remain. No direct REC, white painting, OSD, fastText or model training is included.
- Feature3 requires explicit verified input preparation with examples/prepare_verified_ocr_input.py and examples/ocr_verified_input_repairs.json. It does not automatically repair arbitrary Form bounds in to_markdown. Source PDFs remain untouched.
- Current writeback fonts are finite. Additional fonts require confirmed actual glyph/writeback loss, reproduction and regression checks. Same-result ownership is in memory; reopening spacing and unsupported script combinations retain the documented limits.

## Current evaluation

Same507PDF/509pages per arm; CF506/SF476 supported456defined; official scorer8c63e84. RapidOCR3.10.0 PPv6small DET/REC; OCR150DPI inherited pixel cap; use_ocr=True,force_ocr=False,force_text=True,ocr_language=eng,render_html_tables=None. Two current source arms were freshly extracted; exact RGB/model/config recognition and exact full-output/case/scorer scores were verified before reuse.
- Fixed-main P2+ODM reference: CF79.6709088%/SF56.6573495%; preceding fresh remote validation.
- P2+ODM with approved corrections1,2,3,4,6,7: CF81.9120785%/SF57.9868410%; main delta+2.2411698/+1.3294915pp; selected/Rapid pages237/237.
- IMF2 ROI with approved corrections1,2,3,4,6,7: CF82.6712653%/SF58.7090060%; main delta+3.0003565/+2.0516565pp; selected/Rapid pages307/307.
- Same-correction selector effect IMF2 minus P2: CF+0.7591868pp/SF+0.7221650pp.
- Fresh public outputs1014; actual new DET/REC inputs0; verified recognition reuses544. Official workers0 new;1107 previous unique scores validated. No old Markdown output was substituted for the new public runs.
- Observed extraction validation wall sum291.29s; scoring/reaggregation5.37s. Four workers/startup/tracing and recognition/score reuse are included. These are validation costs, not independent product latency or speed rankings.
- Strict remaining-branch composition reproduces all507 Markdown outputs,509 decision tuples and Rapid RGB inputs of the previously scored without5 arm. New71-test integration profile passed; explicit absence of unconditional Unicode priority is covered. Prior76 tests belonged to the historical full0-7 profile.

## Reproduction

Use a compatible existing draft-2.0 native runtime (tested MuPDF1.28.5), paired source branches and Rapid3.10 models. Python-only source overlay; no native rebuild, wheel publication or package installation was performed.

python examples/build_source_overlay.py --core-repo /path/to/PyMuPDF --native-package /path/to/existing/pymupdf --output /new/path/ocr-runtime

PYTHONPATH=/new/path/ocr-runtime python examples/check_integrated_ocr.py --core-repo /path/to/PyMuPDF

PYTHONPATH=/new/path/ocr-runtime python examples/run_integrated_ocr.py input.pdf /new/path/output.md --input-rules examples/ocr_verified_input_repairs.json

Append --selector p2-odm only for the same-correction comparison adapter; this is not a new public API. The pinned local benchmark/protocol/environment/source hashes are under runs/OCR_INTEGRATION_EXCLUDE_UNICODE_20261031 in the pb_ocr research workspace.

## Complete current improvement/regression cases

Every changed document is listed below. CF/SF are document-level percentages; changes are percentage points. Single-page cases identify page1; multi-page aggregate scores are not attributed to one page. OCR activity is execution evidence, not proof that recognition is correct.

### Approved corrections1,2,3,4,6,7 versus main

Before:main; after:without5-p2.
- CF: improved57, regressed18, unchanged431.
- SF: improved19, regressed5, unchanged432.

- text/text_handwritting__contract; PDF page1.
  Input:docs/text/text_handwritting__contract.pdf.
  CF: 30.5309% -> 48.5736% (+18.0427pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_handwritting__signatures; PDF page1.
  Input:docs/text/text_handwritting__signatures.pdf.
  CF: 36.4002% -> 55.4796% (+19.0793pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__colorprofile; PDF page1.
  Input:docs/text/text_misc__colorprofile.pdf.
  CF: 38.0952% -> 73.9850% (+35.8898pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__missing; PDF page1.
  Input:docs/text/text_misc__missing.pdf.
  CF: 78.4066% -> 86.0067% (+7.6001pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__redacted; PDF page1.
  Input:docs/text/text_misc__redacted.pdf.
  CF: 81.7151% -> 80.9245% (-0.7907pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__redacted3; PDF page1.
  Input:docs/text/text_misc__redacted3.pdf.
  CF: 87.2416% -> 79.1084% (-8.1332pp; regressed).
  SF: 48.3871% -> 0.0000% (-48.3871pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__10k2col; PDF page1.
  Input:docs/text/text_multicolumns__10k2col.pdf.
  CF: 91.3701% -> 91.9813% (+0.6112pp; improved).
  SF: 25.0000% -> 25.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__2col; PDF page1.
  Input:docs/text/text_multicolumns__2col.pdf.
  CF: 0.0000% -> 79.3136% (+79.3136pp; improved).
  SF: 0.0000% -> 60.2617% (+60.2617pp; improved).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__2pages; PDF page1.
  Input:docs/text/text_multicolumns__2pages.pdf.
  CF: 0.0000% -> 90.5557% (+90.5557pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3colP; PDF page1.
  Input:docs/text/text_multicolumns__3colP.pdf.
  CF: 46.8622% -> 46.6890% (-0.1733pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__3col_statment; PDF page1.
  Input:docs/text/text_multicolumns__3col_statment.pdf.
  CF: 80.9526% -> 81.1062% (+0.1536pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__3colsbeluga; PDF page1.
  Input:docs/text/text_multicolumns__3colsbeluga.pdf.
  CF: 96.2322% -> 96.5985% (+0.3663pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__4colimg; PDF page1.
  Input:docs/text/text_multicolumns__4colimg.pdf.
  CF: 0.0000% -> 97.8192% (+97.8192pp; improved).
  SF: 0.0000% -> 50.0000% (+50.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__analysis; PDF page1.
  Input:docs/text/text_multicolumns__analysis.pdf.
  CF: 87.3326% -> 89.9853% (+2.6527pp; improved).
  SF: 97.7528% -> 97.7528% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__battery; PDF page1.
  Input:docs/text/text_multicolumns__battery.pdf.
  CF: 99.2610% -> 98.9697% (-0.2913pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__coorp; PDF page1.
  Input:docs/text/text_multicolumns__coorp.pdf.
  CF: 87.0256% -> 87.2711% (+0.2455pp; improved).
  SF: 98.7805% -> 98.7805% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__dafta; PDF page1.
  Input:docs/text/text_multicolumns__dafta.pdf.
  CF: 91.2683% -> 91.1638% (-0.1045pp; regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__elpais; PDF page1.
  Input:docs/text/text_multicolumns__elpais.pdf.
  CF: 70.0184% -> 70.2900% (+0.2716pp; improved).
  SF: 14.1807% -> 14.1807% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__ethbottens; PDF page1.
  Input:docs/text/text_multicolumns__ethbottens.pdf.
  CF: 77.0392% -> 49.8925% (-27.1467pp; regressed).
  SF: 81.2500% -> 64.2045% (-17.0455pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__japanesefrench; PDF page1.
  Input:docs/text/text_multicolumns__japanesefrench.pdf.
  CF: 72.3819% -> 72.4608% (+0.0789pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__pap_2col; PDF page1.
  Input:docs/text/text_multicolumns__pap_2col.pdf.
  CF: 86.2349% -> 88.0655% (+1.8306pp; improved).
  SF: 79.1246% -> 79.1246% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__paper2; PDF page1.
  Input:docs/text/text_multicolumns__paper2.pdf.
  CF: 91.7413% -> 94.7084% (+2.9671pp; improved).
  SF: 29.1667% -> 29.1667% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__paperchem; PDF page1.
  Input:docs/text/text_multicolumns__paperchem.pdf.
  CF: 64.4459% -> 70.3823% (+5.9364pp; improved).
  SF: 36.1570% -> 44.3723% (+8.2153pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__pwc; PDF page1.
  Input:docs/text/text_multicolumns__pwc.pdf.
  CF: 35.5949% -> 55.5444% (+19.9495pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__enfr; PDF page1.
  Input:docs/text/text_multilang__enfr.pdf.
  CF: 87.0844% -> 85.5368% (-1.5477pp; regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__khazak; PDF page1.
  Input:docs/text/text_multilang__khazak.pdf.
  CF: 46.6742% -> 46.5003% (-0.1739pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__mandarin4; PDF page1.
  Input:docs/text/text_multilang__mandarin4.pdf.
  CF: 26.7394% -> 63.0826% (+36.3432pp; improved).
  SF: 50.0000% -> 87.5000% (+37.5000pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__spanish; PDF page1.
  Input:docs/text/text_multilang__spanish.pdf.
  CF: 82.0444% -> 92.8244% (+10.7800pp; improved).
  SF: 83.4783% -> 83.4783% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multilang__spanish2; PDF page1.
  Input:docs/text/text_multilang__spanish2.pdf.
  CF: 93.6877% -> 95.3700% (+1.6824pp; improved).
  SF: 25.0000% -> 25.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multilang__tegulu; PDF page1.
  Input:docs/text/text_multilang__tegulu.pdf.
  CF: 32.5427% -> 32.6554% (+0.1126pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__turkish; PDF page1.
  Input:docs/text/text_multilang__turkish.pdf.
  CF: 89.3778% -> 90.5091% (+1.1313pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multilang__ukrainian; PDF page1.
  Input:docs/text/text_multilang__ukrainian.pdf.
  CF: 93.1378% -> 95.1430% (+2.0052pp; improved).
  SF: 88.0208% -> 88.0208% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_ocr__069; PDF page1.
  Input:docs/text/text_ocr__069.pdf.
  CF: 36.1432% -> 79.2167% (+43.0735pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__2pages; PDF page1.
  Input:docs/text/text_ocr__2pages.pdf.
  CF: 59.0716% -> 85.0408% (+25.9692pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__9; PDF page1.
  Input:docs/text/text_ocr__9.pdf.
  CF: 62.1733% -> 64.2655% (+2.0922pp; improved).
  SF: 0.0000% -> 8.3333% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__File0021; PDF page1.
  Input:docs/text/text_ocr__File0021.pdf.
  CF: 56.4770% -> 74.0143% (+17.5373pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__abstract; PDF page1.
  Input:docs/text/text_ocr__abstract.pdf.
  CF: 97.5188% -> 85.2618% (-12.2570pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__admnh; PDF page1.
  Input:docs/text/text_ocr__admnh.pdf.
  CF: 83.9142% -> 86.3518% (+2.4376pp; improved).
  SF: 81.2500% -> 81.2500% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__archive; PDF page1.
  Input:docs/text/text_ocr__archive.pdf.
  CF: 39.3527% -> 50.2913% (+10.9386pp; improved).
  SF: 66.6667% -> 75.0000% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__attendence; PDF page1.
  Input:docs/text/text_ocr__attendence.pdf.
  CF: 32.6896% -> 78.7769% (+46.0873pp; improved).
  SF: 0.0000% -> 8.3333% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__blurry; PDF page1.
  Input:docs/text/text_ocr__blurry.pdf.
  CF: 39.0605% -> 70.9002% (+31.8397pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__blurry2; PDF page1.
  Input:docs/text/text_ocr__blurry2.pdf.
  CF: 33.7785% -> 50.8697% (+17.0912pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__bold; PDF page1.
  Input:docs/text/text_ocr__bold.pdf.
  CF: 76.4630% -> 70.9869% (-5.4761pp; regressed).
  SF: 87.5000% -> 0.0000% (-87.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__cert_of_assistanvce; PDF page1.
  Input:docs/text/text_ocr__cert_of_assistanvce.pdf.
  CF: 37.3329% -> 56.8890% (+19.5561pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__christmass; PDF page1.
  Input:docs/text/text_ocr__christmass.pdf.
  CF: 96.0868% -> 95.1979% (-0.8888pp; regressed).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__code; PDF page1.
  Input:docs/text/text_ocr__code.pdf.
  CF: 36.1675% -> 73.8302% (+37.6627pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__cyber; PDF page1.
  Input:docs/text/text_ocr__cyber.pdf.
  CF: 87.3672% -> 92.3587% (+4.9915pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__das; PDF page1.
  Input:docs/text/text_ocr__das.pdf.
  CF: 38.7711% -> 46.0062% (+7.2350pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__data; PDF page1.
  Input:docs/text/text_ocr__data.pdf.
  CF: 96.5644% -> 95.9161% (-0.6483pp; regressed).
  SF: 20.8333% -> 91.6667% (+70.8333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__diseeas; PDF page1.
  Input:docs/text/text_ocr__diseeas.pdf.
  CF: 95.9877% -> 80.6396% (-15.3481pp; regressed).
  SF: 9.8214% -> 88.0952% (+78.2738pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__eller; PDF page1.
  Input:docs/text/text_ocr__eller.pdf.
  CF: 21.3800% -> 91.8295% (+70.4496pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__fpl; PDF page1.
  Input:docs/text/text_ocr__fpl.pdf.
  CF: 72.2005% -> 92.5914% (+20.3909pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__glitch; PDF page1.
  Input:docs/text/text_ocr__glitch.pdf.
  CF: 75.9144% -> 78.3769% (+2.4625pp; improved).
  SF: 13.0682% -> 13.0682% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__inr; PDF page1.
  Input:docs/text/text_ocr__inr.pdf.
  CF: 66.3401% -> 94.7199% (+28.3798pp; improved).
  SF: 16.6667% -> 52.3810% (+35.7143pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__letter; PDF page1.
  Input:docs/text/text_ocr__letter.pdf.
  CF: 46.6693% -> 76.5078% (+29.8385pp; improved).
  SF: 0.0000% -> 78.4903% (+78.4903pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__orientedtex; PDF page1.
  Input:docs/text/text_ocr__orientedtex.pdf.
  CF: 34.8214% -> 47.3520% (+12.5305pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__p4013; PDF page1.
  Input:docs/text/text_ocr__p4013.pdf.
  CF: 92.1540% -> 90.8797% (-1.2742pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__parent; PDF page1.
  Input:docs/text/text_ocr__parent.pdf.
  CF: 98.1859% -> 99.0930% (+0.9070pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__pol; PDF page1.
  Input:docs/text/text_ocr__pol.pdf.
  CF: 52.9425% -> 81.6009% (+28.6584pp; improved).
  SF: 0.0000% -> 2.7778% (+2.7778pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__polishlike; PDF page1.
  Input:docs/text/text_ocr__polishlike.pdf.
  CF: 35.6470% -> 88.9227% (+53.2757pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__pretest; PDF page1.
  Input:docs/text/text_ocr__pretest.pdf.
  CF: 93.0461% -> 79.6841% (-13.3620pp; regressed).
  SF: 100.0000% -> 0.0000% (-100.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__ref; PDF page1.
  Input:docs/text/text_ocr__ref.pdf.
  CF: 72.1914% -> 72.1982% (+0.0067pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__routier; PDF page1.
  Input:docs/text/text_ocr__routier.pdf.
  CF: 80.8308% -> 84.6028% (+3.7720pp; improved).
  SF: 0.0000% -> 38.3333% (+38.3333pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__scanbook; PDF page1.
  Input:docs/text/text_ocr__scanbook.pdf.
  CF: 0.0000% -> 71.4371% (+71.4371pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__secretaria; PDF page1.
  Input:docs/text/text_ocr__secretaria.pdf.
  CF: 68.1164% -> 92.7423% (+24.6259pp; improved).
  SF: 15.6250% -> 21.8750% (+6.2500pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__skew; PDF page1.
  Input:docs/text/text_ocr__skew.pdf.
  CF: 37.7354% -> 87.7469% (+50.0116pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__sup; PDF page1.
  Input:docs/text/text_ocr__sup.pdf.
  CF: 58.3444% -> 79.7251% (+21.3807pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__tata; PDF page1.
  Input:docs/text/text_ocr__tata.pdf.
  CF: 40.7096% -> 78.4876% (+37.7780pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__tridimensional; PDF page1.
  Input:docs/text/text_ocr__tridimensional.pdf.
  CF: 76.1507% -> 76.8015% (+0.6508pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__yellowtype; PDF page1.
  Input:docs/text/text_ocr__yellowtype.pdf.
  CF: 91.0155% -> 87.9665% (-3.0490pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__zaposlitve; PDF page1.
  Input:docs/text/text_ocr__zaposlitve.pdf.
  CF: 53.9199% -> 55.7589% (+1.8390pp; improved).
  SF: 41.4969% -> 0.0000% (-41.4969pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__Preview; PDF page1.
  Input:docs/text/text_simple__Preview.pdf.
  CF: 97.5813% -> 96.9836% (-0.5976pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_simple__att10k; PDF page1.
  Input:docs/text/text_simple__att10k.pdf.
  CF: 62.4997% -> 88.8516% (+26.3519pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_simple__grayson; PDF page1.
  Input:docs/text/text_simple__grayson.pdf.
  CF: 38.0952% -> 76.9421% (+38.8468pp; improved).
  SF: 0.0000% -> 9.0278% (+9.0278pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__listwarnings; PDF page1.
  Input:docs/text/text_simple__listwarnings.pdf.
  CF: 98.6875% -> 98.4581% (-0.2295pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

### Approved integration0,1,2,3,4,6,7 versus main

Before:main; after:without5-imf2.
- CF: improved76, regressed37, unchanged393.
- SF: improved33, regressed12, unchanged411.

- text/text_dense__leaflet; PDF page1.
  Input:docs/text/text_dense__leaflet.pdf.
  CF: 92.8562% -> 91.8862% (-0.9700pp; regressed).
  SF: 60.6838% -> 68.2234% (+7.5397pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_dense__underline; PDF page1.
  Input:docs/text/text_dense__underline.pdf.
  CF: 42.7530% -> 47.8268% (+5.0738pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_handwritting__contract; PDF page1.
  Input:docs/text/text_handwritting__contract.pdf.
  CF: 30.5309% -> 48.5736% (+18.0427pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_handwritting__jp; PDF page1.
  Input:docs/text/text_handwritting__jp.pdf.
  CF: 0.0000% -> 27.0721% (+27.0721pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_handwritting__signatures; PDF page1.
  Input:docs/text/text_handwritting__signatures.pdf.
  CF: 36.4002% -> 55.4796% (+19.0793pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__colorprofile; PDF page1.
  Input:docs/text/text_misc__colorprofile.pdf.
  CF: 38.0952% -> 73.9850% (+35.8898pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__gridofimages; PDF page1.
  Input:docs/text/text_misc__gridofimages.pdf.
  CF: 65.9550% -> 65.3347% (-0.6203pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__ikea3; PDF page1.
  Input:docs/text/text_misc__ikea3.pdf.
  CF: 77.3498% -> 76.7650% (-0.5848pp; regressed).
  SF: 46.5186% -> 35.0055% (-11.5132pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__json; PDF page1.
  Input:docs/text/text_misc__json.pdf.
  CF: 89.1242% -> 88.8427% (-0.2814pp; regressed).
  SF: 83.3333% -> 83.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__redacted; PDF page1.
  Input:docs/text/text_misc__redacted.pdf.
  CF: 81.7151% -> 80.9245% (-0.7907pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__redacted3; PDF page1.
  Input:docs/text/text_misc__redacted3.pdf.
  CF: 87.2416% -> 79.1084% (-8.1332pp; regressed).
  SF: 48.3871% -> 0.0000% (-48.3871pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__10k2col; PDF page1.
  Input:docs/text/text_multicolumns__10k2col.pdf.
  CF: 91.3701% -> 91.9813% (+0.6112pp; improved).
  SF: 25.0000% -> 25.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__2col; PDF page1.
  Input:docs/text/text_multicolumns__2col.pdf.
  CF: 0.0000% -> 79.3136% (+79.3136pp; improved).
  SF: 0.0000% -> 60.2617% (+60.2617pp; improved).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__2col_fund_summary; PDF page1.
  Input:docs/text/text_multicolumns__2col_fund_summary.pdf.
  CF: 99.7445% -> 99.2857% (-0.4587pp; regressed).
  SF: 100.0000% -> 90.0000% (-10.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__2colrep; PDF page1.
  Input:docs/text/text_multicolumns__2colrep.pdf.
  CF: 97.2987% -> 97.0520% (-0.2467pp; regressed).
  SF: 36.6071% -> 36.6071% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__2pages; PDF page1.
  Input:docs/text/text_multicolumns__2pages.pdf.
  CF: 0.0000% -> 90.5557% (+90.5557pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__2x; PDF page1.
  Input:docs/text/text_multicolumns__2x.pdf.
  CF: 89.9595% -> 92.4154% (+2.4559pp; improved).
  SF: 98.7421% -> 61.2421% (-37.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3colP; PDF page1.
  Input:docs/text/text_multicolumns__3colP.pdf.
  CF: 46.8622% -> 46.6890% (-0.1733pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__3col_statment; PDF page1.
  Input:docs/text/text_multicolumns__3col_statment.pdf.
  CF: 80.9526% -> 83.5753% (+2.6227pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3colpres; PDF page1.
  Input:docs/text/text_multicolumns__3colpres.pdf.
  CF: 94.6715% -> 88.4797% (-6.1917pp; regressed).
  SF: 62.5000% -> 62.5000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__4colimg; PDF page1.
  Input:docs/text/text_multicolumns__4colimg.pdf.
  CF: 0.0000% -> 97.8192% (+97.8192pp; improved).
  SF: 0.0000% -> 50.0000% (+50.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__analysis; PDF page1.
  Input:docs/text/text_multicolumns__analysis.pdf.
  CF: 87.3326% -> 89.9853% (+2.6527pp; improved).
  SF: 97.7528% -> 97.7528% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__article; PDF page1.
  Input:docs/text/text_multicolumns__article.pdf.
  CF: 90.9122% -> 90.8697% (-0.0425pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__battery; PDF page1.
  Input:docs/text/text_multicolumns__battery.pdf.
  CF: 99.2610% -> 98.9697% (-0.2913pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__coorp; PDF page1.
  Input:docs/text/text_multicolumns__coorp.pdf.
  CF: 87.0256% -> 96.3423% (+9.3167pp; improved).
  SF: 98.7805% -> 98.7805% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__dafta; PDF page1.
  Input:docs/text/text_multicolumns__dafta.pdf.
  CF: 91.2683% -> 92.3889% (+1.1206pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__drill; PDF page1.
  Input:docs/text/text_multicolumns__drill.pdf.
  CF: 93.0219% -> 96.5135% (+3.4916pp; improved).
  SF: 66.6667% -> 58.3333% (-8.3333pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__elpais; PDF page1.
  Input:docs/text/text_multicolumns__elpais.pdf.
  CF: 70.0184% -> 70.2900% (+0.2716pp; improved).
  SF: 14.1807% -> 14.1807% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__energy2; PDF page1.
  Input:docs/text/text_multicolumns__energy2.pdf.
  CF: 85.4816% -> 93.6204% (+8.1388pp; improved).
  SF: 99.1071% -> 86.6071% (-12.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__esd_end; PDF page1.
  Input:docs/text/text_multicolumns__esd_end.pdf.
  CF: 84.0375% -> 83.6335% (-0.4040pp; regressed).
  SF: 47.9167% -> 0.0000% (-47.9167pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__esg_whitespace; PDF page1.
  Input:docs/text/text_multicolumns__esg_whitespace.pdf.
  CF: 97.6057% -> 97.0178% (-0.5879pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__forword2cols; PDF page1.
  Input:docs/text/text_multicolumns__forword2cols.pdf.
  CF: 96.9225% -> 88.4971% (-8.4254pp; regressed).
  SF: 100.0000% -> 50.0000% (-50.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__heirloom; PDF page1.
  Input:docs/text/text_multicolumns__heirloom.pdf.
  CF: 38.0952% -> 49.1258% (+11.0305pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__japanesefrench; PDF page1.
  Input:docs/text/text_multicolumns__japanesefrench.pdf.
  CF: 72.3819% -> 72.4608% (+0.0789pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__pap_2col; PDF page1.
  Input:docs/text/text_multicolumns__pap_2col.pdf.
  CF: 86.2349% -> 88.0655% (+1.8306pp; improved).
  SF: 79.1246% -> 79.1246% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__paper2; PDF page1.
  Input:docs/text/text_multicolumns__paper2.pdf.
  CF: 91.7413% -> 94.7084% (+2.9671pp; improved).
  SF: 29.1667% -> 29.1667% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_multicolumns__pwc; PDF page1.
  Input:docs/text/text_multicolumns__pwc.pdf.
  CF: 35.5949% -> 55.5444% (+19.9495pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multicolumns__sbi; PDF page1.
  Input:docs/text/text_multicolumns__sbi.pdf.
  CF: 95.7029% -> 95.6861% (-0.0168pp; regressed).
  SF: 41.6667% -> 41.6667% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__tableOfContent8col; PDF page1.
  Input:docs/text/text_multicolumns__tableOfContent8col.pdf.
  CF: 62.0923% -> 60.3025% (-1.7898pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__tableinmiddle2cols; PDF page1.
  Input:docs/text/text_multicolumns__tableinmiddle2cols.pdf.
  CF: 57.7184% -> 82.5286% (+24.8102pp; improved).
  SF: 0.0000% -> 11.2500% (+11.2500pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__visa; PDF page1.
  Input:docs/text/text_multicolumns__visa.pdf.
  CF: 87.3084% -> 91.4557% (+4.1473pp; improved).
  SF: 0.0000% -> 83.3333% (+83.3333pp; improved).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__waterfal; PDF page1.
  Input:docs/text/text_multicolumns__waterfal.pdf.
  CF: 94.3911% -> 79.6930% (-14.6981pp; regressed).
  SF: 68.3333% -> 68.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__weeds; PDF page1.
  Input:docs/text/text_multicolumns__weeds.pdf.
  CF: 99.2353% -> 99.0645% (-0.1708pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__cnnm; PDF page1.
  Input:docs/text/text_multilang__cnnm.pdf.
  CF: 57.1429% -> 65.9864% (+8.8435pp; improved).
  SF: 0.0000% -> 41.6667% (+41.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__greek; PDF page1.
  Input:docs/text/text_multilang__greek.pdf.
  CF: 87.7175% -> 95.9455% (+8.2279pp; improved).
  SF: 25.0000% -> 83.3333% (+58.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__japanese5; PDF page1.
  Input:docs/text/text_multilang__japanese5.pdf.
  CF: 25.2019% -> 25.1959% (-0.0060pp; regressed).
  SF: 44.9597% -> 47.8414% (+2.8817pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__kannada; PDF page1.
  Input:docs/text/text_multilang__kannada.pdf.
  CF: 30.3700% -> 30.6963% (+0.3263pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__khazak; PDF page1.
  Input:docs/text/text_multilang__khazak.pdf.
  CF: 46.6742% -> 46.5003% (-0.1739pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__mandarin4; PDF page1.
  Input:docs/text/text_multilang__mandarin4.pdf.
  CF: 26.7394% -> 63.0826% (+36.3432pp; improved).
  SF: 50.0000% -> 87.5000% (+37.5000pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__romanian; PDF page1.
  Input:docs/text/text_multilang__romanian.pdf.
  CF: 84.5501% -> 85.4180% (+0.8679pp; improved).
  SF: 91.8681% -> 87.0879% (-4.7802pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__spanish; PDF page1.
  Input:docs/text/text_multilang__spanish.pdf.
  CF: 82.0444% -> 92.5283% (+10.4839pp; improved).
  SF: 83.4783% -> 83.4783% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__spanish2; PDF page1.
  Input:docs/text/text_multilang__spanish2.pdf.
  CF: 93.6877% -> 95.3700% (+1.6824pp; improved).
  SF: 25.0000% -> 37.5000% (+12.5000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__tegulu; PDF page1.
  Input:docs/text/text_multilang__tegulu.pdf.
  CF: 32.5427% -> 32.6554% (+0.1126pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_multilang__turkish; PDF page1.
  Input:docs/text/text_multilang__turkish.pdf.
  CF: 89.3778% -> 91.6040% (+2.2262pp; improved).
  SF: 0.0000% -> 41.6667% (+41.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__ukrainian; PDF page1.
  Input:docs/text/text_multilang__ukrainian.pdf.
  CF: 93.1378% -> 94.7894% (+1.6516pp; improved).
  SF: 88.0208% -> 88.0208% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__069; PDF page1.
  Input:docs/text/text_ocr__069.pdf.
  CF: 36.1432% -> 79.2167% (+43.0735pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__2pages; PDF page1.
  Input:docs/text/text_ocr__2pages.pdf.
  CF: 59.0716% -> 85.0408% (+25.9692pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__9; PDF page1.
  Input:docs/text/text_ocr__9.pdf.
  CF: 62.1733% -> 64.2655% (+2.0922pp; improved).
  SF: 0.0000% -> 8.3333% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__File0021; PDF page1.
  Input:docs/text/text_ocr__File0021.pdf.
  CF: 56.4770% -> 74.0143% (+17.5373pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__archive; PDF page1.
  Input:docs/text/text_ocr__archive.pdf.
  CF: 39.3527% -> 50.2913% (+10.9386pp; improved).
  SF: 66.6667% -> 75.0000% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__attendence; PDF page1.
  Input:docs/text/text_ocr__attendence.pdf.
  CF: 32.6896% -> 78.7769% (+46.0873pp; improved).
  SF: 0.0000% -> 8.3333% (+8.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__blurry; PDF page1.
  Input:docs/text/text_ocr__blurry.pdf.
  CF: 39.0605% -> 70.9002% (+31.8397pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__blurry2; PDF page1.
  Input:docs/text/text_ocr__blurry2.pdf.
  CF: 33.7785% -> 50.8697% (+17.0912pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__bold; PDF page1.
  Input:docs/text/text_ocr__bold.pdf.
  CF: 76.4630% -> 70.9869% (-5.4761pp; regressed).
  SF: 87.5000% -> 0.0000% (-87.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__cert_of_assistanvce; PDF page1.
  Input:docs/text/text_ocr__cert_of_assistanvce.pdf.
  CF: 37.3329% -> 56.8890% (+19.5561pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__christmass; PDF page1.
  Input:docs/text/text_ocr__christmass.pdf.
  CF: 96.0868% -> 95.1979% (-0.8888pp; regressed).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__code; PDF page1.
  Input:docs/text/text_ocr__code.pdf.
  CF: 36.1675% -> 73.8302% (+37.6627pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__cyber; PDF page1.
  Input:docs/text/text_ocr__cyber.pdf.
  CF: 87.3672% -> 92.3587% (+4.9915pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__data; PDF page1.
  Input:docs/text/text_ocr__data.pdf.
  CF: 96.5644% -> 95.9161% (-0.6483pp; regressed).
  SF: 20.8333% -> 91.6667% (+70.8333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__eller; PDF page1.
  Input:docs/text/text_ocr__eller.pdf.
  CF: 21.3800% -> 91.8295% (+70.4496pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__fpl; PDF page1.
  Input:docs/text/text_ocr__fpl.pdf.
  CF: 72.2005% -> 92.5914% (+20.3909pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__glitch; PDF page1.
  Input:docs/text/text_ocr__glitch.pdf.
  CF: 75.9144% -> 78.3769% (+2.4625pp; improved).
  SF: 13.0682% -> 13.0682% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__inr; PDF page1.
  Input:docs/text/text_ocr__inr.pdf.
  CF: 66.3401% -> 94.7199% (+28.3798pp; improved).
  SF: 16.6667% -> 52.3810% (+35.7143pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__klein; PDF page1.
  Input:docs/text/text_ocr__klein.pdf.
  CF: 45.0749% -> 60.3002% (+15.2253pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__letter; PDF page1.
  Input:docs/text/text_ocr__letter.pdf.
  CF: 46.6693% -> 76.5078% (+29.8385pp; improved).
  SF: 0.0000% -> 78.4903% (+78.4903pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__mag; PDF page1.
  Input:docs/text/text_ocr__mag.pdf.
  CF: 0.0000% -> 73.3805% (+73.3805pp; improved).
  SF: 0.0000% -> 26.3158% (+26.3158pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__orientedtex; PDF page1.
  Input:docs/text/text_ocr__orientedtex.pdf.
  CF: 34.8214% -> 47.3520% (+12.5305pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__p4013; PDF page1.
  Input:docs/text/text_ocr__p4013.pdf.
  CF: 92.1540% -> 90.8797% (-1.2742pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__parent; PDF page1.
  Input:docs/text/text_ocr__parent.pdf.
  CF: 98.1859% -> 99.0930% (+0.9070pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__pol; PDF page1.
  Input:docs/text/text_ocr__pol.pdf.
  CF: 52.9425% -> 81.6009% (+28.6584pp; improved).
  SF: 0.0000% -> 2.7778% (+2.7778pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__polishlike; PDF page1.
  Input:docs/text/text_ocr__polishlike.pdf.
  CF: 35.6470% -> 88.9227% (+53.2757pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__pretest; PDF page1.
  Input:docs/text/text_ocr__pretest.pdf.
  CF: 93.0461% -> 79.6841% (-13.3620pp; regressed).
  SF: 100.0000% -> 0.0000% (-100.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__ref; PDF page1.
  Input:docs/text/text_ocr__ref.pdf.
  CF: 72.1914% -> 72.1982% (+0.0067pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__routier; PDF page1.
  Input:docs/text/text_ocr__routier.pdf.
  CF: 80.8308% -> 84.6028% (+3.7720pp; improved).
  SF: 0.0000% -> 38.3333% (+38.3333pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_ocr__scanbook; PDF page1.
  Input:docs/text/text_ocr__scanbook.pdf.
  CF: 0.0000% -> 71.4371% (+71.4371pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__scaninfile; PDF page1.
  Input:docs/text/text_ocr__scaninfile.pdf.
  CF: 0.0000% -> 76.1763% (+76.1763pp; improved).
  SF: 0.0000% -> 40.2778% (+40.2778pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__secretaria; PDF page1.
  Input:docs/text/text_ocr__secretaria.pdf.
  CF: 68.1164% -> 92.7423% (+24.6259pp; improved).
  SF: 15.6250% -> 21.8750% (+6.2500pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__skew; PDF page1.
  Input:docs/text/text_ocr__skew.pdf.
  CF: 37.7354% -> 87.7469% (+50.0116pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__sup; PDF page1.
  Input:docs/text/text_ocr__sup.pdf.
  CF: 58.3444% -> 79.7251% (+21.3807pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__tata; PDF page1.
  Input:docs/text/text_ocr__tata.pdf.
  CF: 40.7096% -> 78.4876% (+37.7780pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__tridimensional; PDF page1.
  Input:docs/text/text_ocr__tridimensional.pdf.
  CF: 76.1507% -> 76.8015% (+0.6508pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__yellowtype; PDF page1.
  Input:docs/text/text_ocr__yellowtype.pdf.
  CF: 91.0155% -> 87.9665% (-3.0490pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__zaposlitve; PDF page1.
  Input:docs/text/text_ocr__zaposlitve.pdf.
  CF: 53.9199% -> 55.7589% (+1.8390pp; improved).
  SF: 41.4969% -> 0.0000% (-41.4969pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__4g; PDF page1.
  Input:docs/text/text_simple__4g.pdf.
  CF: 96.5070% -> 97.3875% (+0.8805pp; improved).
  SF: 82.3718% -> 82.3718% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__Preview; PDF page1.
  Input:docs/text/text_simple__Preview.pdf.
  CF: 97.5813% -> 96.9836% (-0.5976pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_simple__adminplan; PDF page1.
  Input:docs/text/text_simple__adminplan.pdf.
  CF: 87.0748% -> 98.6395% (+11.5646pp; improved).
  SF: 0.0000% -> 66.6667% (+66.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__att10k; PDF page1.
  Input:docs/text/text_simple__att10k.pdf.
  CF: 62.4997% -> 88.8516% (+26.3519pp; improved).
  Selected pages:[1]->[1]; Rapid pages:[1]->[1]; Markdown changed:True.

- text/text_simple__bottens; PDF page1.
  Input:docs/text/text_simple__bottens.pdf.
  CF: 99.0257% -> 98.6575% (-0.3682pp; regressed).
  SF: 93.3036% -> 93.3036% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__delinea; PDF page1.
  Input:docs/text/text_simple__delinea.pdf.
  CF: 93.8443% -> 93.5589% (-0.2854pp; regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__finra; PDF page1.
  Input:docs/text/text_simple__finra.pdf.
  CF: 41.9132% -> 72.2982% (+30.3850pp; improved).
  SF: 0.0000% -> 22.7273% (+22.7273pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__grayson; PDF page1.
  Input:docs/text/text_simple__grayson.pdf.
  CF: 38.0952% -> 76.9421% (+38.8468pp; improved).
  SF: 0.0000% -> 9.0278% (+9.0278pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__green; PDF page1.
  Input:docs/text/text_simple__green.pdf.
  CF: 66.5353% -> 66.2319% (-0.3034pp; regressed).
  SF: 50.0000% -> 62.5000% (+12.5000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__hex; PDF page1.
  Input:docs/text/text_simple__hex.pdf.
  CF: 88.2647% -> 88.0633% (-0.2014pp; regressed).
  SF: 83.3333% -> 83.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__iehp; PDF page1.
  Input:docs/text/text_simple__iehp.pdf.
  CF: 94.0494% -> 93.5497% (-0.4997pp; regressed).
  SF: 75.0000% -> 75.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__italicsummary; PDF page1.
  Input:docs/text/text_simple__italicsummary.pdf.
  CF: 97.6190% -> 99.2872% (+1.6682pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__landfill; PDF page1.
  Input:docs/text/text_simple__landfill.pdf.
  CF: 38.0952% -> 80.9001% (+42.8048pp; improved).
  SF: 0.0000% -> 32.8020% (+32.8020pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__listwarnings; PDF page1.
  Input:docs/text/text_simple__listwarnings.pdf.
  CF: 98.6875% -> 98.4581% (-0.2295pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[]; Rapid pages:[]->[]; Markdown changed:True.

- text/text_simple__marknotTable; PDF page1.
  Input:docs/text/text_simple__marknotTable.pdf.
  CF: 97.7013% -> 97.2568% (-0.4444pp; regressed).
  SF: 84.4828% -> 84.4828% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__redirect; PDF page1.
  Input:docs/text/text_simple__redirect.pdf.
  CF: 96.0317% -> 94.7036% (-1.3282pp; regressed).
  SF: 95.4545% -> 95.4545% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__references; PDF page1.
  Input:docs/text/text_simple__references.pdf.
  CF: 96.4334% -> 96.0960% (-0.3374pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__state; PDF page1.
  Input:docs/text/text_simple__state.pdf.
  CF: 87.7484% -> 92.2078% (+4.4594pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__tagblatt; PDF page1.
  Input:docs/text/text_simple__tagblatt.pdf.
  CF: 97.4889% -> 97.5427% (+0.0538pp; improved).
  SF: 79.1667% -> 100.0000% (+20.8333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_sparse__conductivity; PDF page1.
  Input:docs/text/text_sparse__conductivity.pdf.
  CF: 60.9524% -> 77.3449% (+16.3925pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

### Selector comparison on identical approved corrections

Before:without5-p2; after:without5-imf2.
- CF: improved31, regressed31, unchanged444.
- SF: improved17, regressed10, unchanged429.

- text/text_dense__leaflet; PDF page1.
  Input:docs/text/text_dense__leaflet.pdf.
  CF: 92.8562% -> 91.8862% (-0.9700pp; regressed).
  SF: 60.6838% -> 68.2234% (+7.5397pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_dense__underline; PDF page1.
  Input:docs/text/text_dense__underline.pdf.
  CF: 42.7530% -> 47.8268% (+5.0738pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_handwritting__jp; PDF page1.
  Input:docs/text/text_handwritting__jp.pdf.
  CF: 0.0000% -> 27.0721% (+27.0721pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__gridofimages; PDF page1.
  Input:docs/text/text_misc__gridofimages.pdf.
  CF: 65.9550% -> 65.3347% (-0.6203pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__ikea3; PDF page1.
  Input:docs/text/text_misc__ikea3.pdf.
  CF: 77.3498% -> 76.7650% (-0.5848pp; regressed).
  SF: 46.5186% -> 35.0055% (-11.5132pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__json; PDF page1.
  Input:docs/text/text_misc__json.pdf.
  CF: 89.1242% -> 88.8427% (-0.2814pp; regressed).
  SF: 83.3333% -> 83.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_misc__missing; PDF page1.
  Input:docs/text/text_misc__missing.pdf.
  CF: 86.0067% -> 78.4066% (-7.6001pp; regressed).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__2col_fund_summary; PDF page1.
  Input:docs/text/text_multicolumns__2col_fund_summary.pdf.
  CF: 99.7445% -> 99.2857% (-0.4587pp; regressed).
  SF: 100.0000% -> 90.0000% (-10.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__2colrep; PDF page1.
  Input:docs/text/text_multicolumns__2colrep.pdf.
  CF: 97.2987% -> 97.0520% (-0.2467pp; regressed).
  SF: 36.6071% -> 36.6071% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__2x; PDF page1.
  Input:docs/text/text_multicolumns__2x.pdf.
  CF: 89.9595% -> 92.4154% (+2.4559pp; improved).
  SF: 98.7421% -> 61.2421% (-37.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3col_statment; PDF page1.
  Input:docs/text/text_multicolumns__3col_statment.pdf.
  CF: 81.1062% -> 83.5753% (+2.4691pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3colpres; PDF page1.
  Input:docs/text/text_multicolumns__3colpres.pdf.
  CF: 94.6715% -> 88.4797% (-6.1917pp; regressed).
  SF: 62.5000% -> 62.5000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__3colsbeluga; PDF page1.
  Input:docs/text/text_multicolumns__3colsbeluga.pdf.
  CF: 96.5985% -> 96.2322% (-0.3663pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__article; PDF page1.
  Input:docs/text/text_multicolumns__article.pdf.
  CF: 90.9122% -> 90.8697% (-0.0425pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__coorp; PDF page1.
  Input:docs/text/text_multicolumns__coorp.pdf.
  CF: 87.2711% -> 96.3423% (+9.0712pp; improved).
  SF: 98.7805% -> 98.7805% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__dafta; PDF page1.
  Input:docs/text/text_multicolumns__dafta.pdf.
  CF: 91.1638% -> 92.3889% (+1.2251pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__drill; PDF page1.
  Input:docs/text/text_multicolumns__drill.pdf.
  CF: 93.0219% -> 96.5135% (+3.4916pp; improved).
  SF: 66.6667% -> 58.3333% (-8.3333pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__energy2; PDF page1.
  Input:docs/text/text_multicolumns__energy2.pdf.
  CF: 85.4816% -> 93.6204% (+8.1388pp; improved).
  SF: 99.1071% -> 86.6071% (-12.5000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__esd_end; PDF page1.
  Input:docs/text/text_multicolumns__esd_end.pdf.
  CF: 84.0375% -> 83.6335% (-0.4040pp; regressed).
  SF: 47.9167% -> 0.0000% (-47.9167pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__esg_whitespace; PDF page1.
  Input:docs/text/text_multicolumns__esg_whitespace.pdf.
  CF: 97.6057% -> 97.0178% (-0.5879pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__ethbottens; PDF page1.
  Input:docs/text/text_multicolumns__ethbottens.pdf.
  CF: 49.8925% -> 77.0392% (+27.1467pp; improved).
  SF: 64.2045% -> 81.2500% (+17.0455pp; improved).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__forword2cols; PDF page1.
  Input:docs/text/text_multicolumns__forword2cols.pdf.
  CF: 96.9225% -> 88.4971% (-8.4254pp; regressed).
  SF: 100.0000% -> 50.0000% (-50.0000pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__heirloom; PDF page1.
  Input:docs/text/text_multicolumns__heirloom.pdf.
  CF: 38.0952% -> 49.1258% (+11.0305pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__paperchem; PDF page1.
  Input:docs/text/text_multicolumns__paperchem.pdf.
  CF: 70.3823% -> 64.4459% (-5.9364pp; regressed).
  SF: 44.3723% -> 36.1570% (-8.2153pp; regressed).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__sbi; PDF page1.
  Input:docs/text/text_multicolumns__sbi.pdf.
  CF: 95.7029% -> 95.6861% (-0.0168pp; regressed).
  SF: 41.6667% -> 41.6667% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__tableOfContent8col; PDF page1.
  Input:docs/text/text_multicolumns__tableOfContent8col.pdf.
  CF: 62.0923% -> 60.3025% (-1.7898pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__tableinmiddle2cols; PDF page1.
  Input:docs/text/text_multicolumns__tableinmiddle2cols.pdf.
  CF: 57.7184% -> 82.5286% (+24.8102pp; improved).
  SF: 0.0000% -> 11.2500% (+11.2500pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__visa; PDF page1.
  Input:docs/text/text_multicolumns__visa.pdf.
  CF: 87.3084% -> 91.4557% (+4.1473pp; improved).
  SF: 0.0000% -> 83.3333% (+83.3333pp; improved).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multicolumns__waterfal; PDF page1.
  Input:docs/text/text_multicolumns__waterfal.pdf.
  CF: 94.3911% -> 79.6930% (-14.6981pp; regressed).
  SF: 68.3333% -> 68.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multicolumns__weeds; PDF page1.
  Input:docs/text/text_multicolumns__weeds.pdf.
  CF: 99.2353% -> 99.0645% (-0.1708pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__cnnm; PDF page1.
  Input:docs/text/text_multilang__cnnm.pdf.
  CF: 57.1429% -> 65.9864% (+8.8435pp; improved).
  SF: 0.0000% -> 41.6667% (+41.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__enfr; PDF page1.
  Input:docs/text/text_multilang__enfr.pdf.
  CF: 85.5368% -> 87.0844% (+1.5477pp; improved).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_multilang__greek; PDF page1.
  Input:docs/text/text_multilang__greek.pdf.
  CF: 87.7175% -> 95.9455% (+8.2279pp; improved).
  SF: 25.0000% -> 83.3333% (+58.3333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__japanese5; PDF page1.
  Input:docs/text/text_multilang__japanese5.pdf.
  CF: 25.2019% -> 25.1959% (-0.0060pp; regressed).
  SF: 44.9597% -> 47.8414% (+2.8817pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__kannada; PDF page1.
  Input:docs/text/text_multilang__kannada.pdf.
  CF: 30.3700% -> 30.6963% (+0.3263pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__romanian; PDF page1.
  Input:docs/text/text_multilang__romanian.pdf.
  CF: 84.5501% -> 85.4180% (+0.8679pp; improved).
  SF: 91.8681% -> 87.0879% (-4.7802pp; regressed).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__spanish; PDF page1.
  Input:docs/text/text_multilang__spanish.pdf.
  CF: 92.8244% -> 92.5283% (-0.2961pp; regressed).
  SF: 83.4783% -> 83.4783% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__spanish2; PDF page1.
  Input:docs/text/text_multilang__spanish2.pdf.
  CF: 95.3700% -> 95.3700% (+0.0000pp; unchanged).
  SF: 25.0000% -> 37.5000% (+12.5000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__turkish; PDF page1.
  Input:docs/text/text_multilang__turkish.pdf.
  CF: 90.5091% -> 91.6040% (+1.0949pp; improved).
  SF: 0.0000% -> 41.6667% (+41.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_multilang__ukrainian; PDF page1.
  Input:docs/text/text_multilang__ukrainian.pdf.
  CF: 95.1430% -> 94.7894% (-0.3536pp; regressed).
  SF: 88.0208% -> 88.0208% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__abstract; PDF page1.
  Input:docs/text/text_ocr__abstract.pdf.
  CF: 85.2618% -> 97.5188% (+12.2570pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_ocr__admnh; PDF page1.
  Input:docs/text/text_ocr__admnh.pdf.
  CF: 86.3518% -> 83.9142% (-2.4376pp; regressed).
  SF: 81.2500% -> 81.2500% (+0.0000pp; unchanged).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_ocr__das; PDF page1.
  Input:docs/text/text_ocr__das.pdf.
  CF: 46.0062% -> 38.7711% (-7.2350pp; regressed).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_ocr__diseeas; PDF page1.
  Input:docs/text/text_ocr__diseeas.pdf.
  CF: 80.6396% -> 95.9877% (+15.3481pp; improved).
  SF: 88.0952% -> 9.8214% (-78.2738pp; regressed).
  Selected pages:[1]->[]; Rapid pages:[1]->[]; Markdown changed:True.

- text/text_ocr__klein; PDF page1.
  Input:docs/text/text_ocr__klein.pdf.
  CF: 45.0749% -> 60.3002% (+15.2253pp; improved).
  SF: 0.0000% -> 0.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__mag; PDF page1.
  Input:docs/text/text_ocr__mag.pdf.
  CF: 0.0000% -> 73.3805% (+73.3805pp; improved).
  SF: 0.0000% -> 26.3158% (+26.3158pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_ocr__scaninfile; PDF page1.
  Input:docs/text/text_ocr__scaninfile.pdf.
  CF: 0.0000% -> 76.1763% (+76.1763pp; improved).
  SF: 0.0000% -> 40.2778% (+40.2778pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__4g; PDF page1.
  Input:docs/text/text_simple__4g.pdf.
  CF: 96.5070% -> 97.3875% (+0.8805pp; improved).
  SF: 82.3718% -> 82.3718% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__adminplan; PDF page1.
  Input:docs/text/text_simple__adminplan.pdf.
  CF: 87.0748% -> 98.6395% (+11.5646pp; improved).
  SF: 0.0000% -> 66.6667% (+66.6667pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__bottens; PDF page1.
  Input:docs/text/text_simple__bottens.pdf.
  CF: 99.0257% -> 98.6575% (-0.3682pp; regressed).
  SF: 93.3036% -> 93.3036% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__delinea; PDF page1.
  Input:docs/text/text_simple__delinea.pdf.
  CF: 93.8443% -> 93.5589% (-0.2854pp; regressed).
  SF: 50.0000% -> 50.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__finra; PDF page1.
  Input:docs/text/text_simple__finra.pdf.
  CF: 41.9132% -> 72.2982% (+30.3850pp; improved).
  SF: 0.0000% -> 22.7273% (+22.7273pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__green; PDF page1.
  Input:docs/text/text_simple__green.pdf.
  CF: 66.5353% -> 66.2319% (-0.3034pp; regressed).
  SF: 50.0000% -> 62.5000% (+12.5000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__hex; PDF page1.
  Input:docs/text/text_simple__hex.pdf.
  CF: 88.2647% -> 88.0633% (-0.2014pp; regressed).
  SF: 83.3333% -> 83.3333% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__iehp; PDF page1.
  Input:docs/text/text_simple__iehp.pdf.
  CF: 94.0494% -> 93.5497% (-0.4997pp; regressed).
  SF: 75.0000% -> 75.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__italicsummary; PDF page1.
  Input:docs/text/text_simple__italicsummary.pdf.
  CF: 97.6190% -> 99.2872% (+1.6682pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__landfill; PDF page1.
  Input:docs/text/text_simple__landfill.pdf.
  CF: 38.0952% -> 80.9001% (+42.8048pp; improved).
  SF: 0.0000% -> 32.8020% (+32.8020pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__marknotTable; PDF page1.
  Input:docs/text/text_simple__marknotTable.pdf.
  CF: 97.7013% -> 97.2568% (-0.4444pp; regressed).
  SF: 84.4828% -> 84.4828% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__redirect; PDF page1.
  Input:docs/text/text_simple__redirect.pdf.
  CF: 96.0317% -> 94.7036% (-1.3282pp; regressed).
  SF: 95.4545% -> 95.4545% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__references; PDF page1.
  Input:docs/text/text_simple__references.pdf.
  CF: 96.4334% -> 96.0960% (-0.3374pp; regressed).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__state; PDF page1.
  Input:docs/text/text_simple__state.pdf.
  CF: 87.7484% -> 92.2078% (+4.4594pp; improved).
  SF: 100.0000% -> 100.0000% (+0.0000pp; unchanged).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_simple__tagblatt; PDF page1.
  Input:docs/text/text_simple__tagblatt.pdf.
  CF: 97.4889% -> 97.5427% (+0.0538pp; improved).
  SF: 79.1667% -> 100.0000% (+20.8333pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

- text/text_sparse__conductivity; PDF page1.
  Input:docs/text/text_sparse__conductivity.pdf.
  CF: 60.9524% -> 77.3449% (+16.3925pp; improved).
  SF: 0.0000% -> 100.0000% (+100.0000pp; improved).
  Selected pages:[]->[1]; Rapid pages:[]->[1]; Markdown changed:True.

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
