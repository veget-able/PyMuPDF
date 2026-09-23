# PyMuPDF Table 기능 명세

2026-09-23 제품 내부 이식: 아래 동결 명세의 PB 외부 활성화 설명은
[제품 내부 경계 문서](native-table-pipeline.md)와 짝 제품의 실행 경로로 대체한다.
PyMuPDF 자체는 ONNX나 PyMuPDF4LLM에 의존하지 않는다.

이 파일은 pb_table의 기능 명세에서 이 저장소의 변경과 필요한 공통 계약을 발췌한 동결본이다.
원문: PB:docs/benchmarks/table-feature-specification.md (2026-09-17). 절 번호는 원문과 같다.
PM=PyMuPDF, LL=PyMuPDF4LLM Table, OCR=별도 OCR 브랜치, PB=pb_table 실행 어댑터다.
다른 저장소 파일/기능을 여기에 이미 내장했다는 뜻은 아니다. 테스트 이름은 저장소 표기를
따르며, 별도 표기가 없는 어댑터 테스트는 PB:tests/에 있다.

커밋 메시지의 Spec 참조는 이 검수 브랜치 최종 상태에 포함된 파일을 가리킨다.
개별 중간 커밋에 모든 의존 소스와 명세가 갖춰져 있다는 뜻은 아니다.
커밋을 따로 적용할 때 Requires와 원문 보존 계약을 함께 확인한다.

## 2. 실행 위치와 기능 간 경계

```text
page text / native rules / image pixels
  -> GNN regions + retained TGIF inputs
  -> ruling candidates + admission
  -> union selection + parent-preservation decision
  -> early residual grid recovery
  -> remaining GNN regions: node-based split -> TGIF
  -> grid refinement / repeated-header split / header-band repair
  -> grid-based split: horizontal slice OR child TGIF + refinement
  -> final header roles per surviving grid
  -> fragment repair / retained-node cell recovery
  -> header roles again ONLY for changed grids
  -> source-backed external Text / HTML / layout normalization
```

모든 검출을 처음 한 번에 끝내고 모든 복원을 한 번만 하는 구조가 아니다.
원본 node 분할은 TGIF 전에, 격자 기반 분할은 셀이 생긴 뒤에야 판단 가능하다.
실제 구현은 scoped hook과 기존 refine 호출을 재사용한다. 위 순서는 의존 관계이며
각 함수가 페이지당 정확히 한 번 실행된다는 보장이 아니다.

특히 현재 **초기 잔여 복원 -> refine/R6 -> 조각 정리 -> 최종 셀 귀속** 순서를 유지한다.
조각 연결을 앞당겨 bbox 내부가 된 틈새 텍스트를 잔여에서 지우는 재배열은 승인되지 않았다.

### 3.1 추가 괘선·박스 입력 전달 — `rule-input-forwarding`

- **문제/역할**: 호출자가 전달한 선·박스가 중첩 union finder에서 빠지면 raster 등의
  추가 근거가 실제 검출에 사용되지 않는다. 기존 `add_lines`/`add_boxes`를 끝까지 전달한다.
- **입출력·위치**: PDF 페이지 좌표의 가상 선/박스 -> union 내부 괘선 후보. 좌표를 새로
  추정하거나, 입력되었다는 이유만으로 후보를 승인하지 않는다.
- **의존/재사용**: 기존 `Page.find_tables` 입력 계약과 후보 생성기 사용. 추가 추론 없음.
- **적용/제거**: 전달 계약 수정으로 항상 적용. 독립 정책 스위치 없음. 제거하면 3.3 등의
  생산자는 존재해도 소비가 끊긴다. 생산 기능과 함께 정리하지 않는 단독 제거는 권하지 않는다.
- **구현/확인**: `PM:src/_table_union.py::_union_line_candidates`,
  `PM:src/table.py::find_tables`; 제품 `tests/test_table_html.py`의 가상 입력 경로.

### 3.2 가는 채움 사각형의 괘선 인식 — `thin-rule-recovery`

- **문제/역할**: PDF가 선을 `line`이 아니라 가는 filled rectangle으로 그리면 strict
  괘선 검출이 이를 버린다. 큰 fill path 안의 개별 얇은 `re`도 선 재료로 보존한다.
- **조건**: 사각형의 짧은 변이 기존 최소 선 길이 기준 이하이고 긴 변보다 짧을 때.
  넓은 배경 사각형 전체를 표 선으로 간주하는 규칙이 아니다.
- **입출력·위치**: 기존 vector drawing items -> `make_edges`의 선 재료.
  전체 path bbox만 보고 판단하지 않는다. 도형 재추출 없이 공용 drawing 결과를 소비한다.
- **적용/제거**: strict 변환 경로의 버그 수정, 별도 스위치 없음. 제거하면 해당 PDF의 선/셀이
  사라질 수 있다. 일반 선 입력은 유지된다. raster 검출과는 별개로 판단할 수 있다.
- **구현/확인**: `PM:src/table.py::_collect_graphic_evidence`, `make_edges`;
  얇은 괘선 사례 (원문 PB:docs/benchmarks 기준 상대 경로: ../experiments/v2-thin-filled-rectangle-cases.md).

### 3.4 근거 부족 괘선 후보의 승인 거절 — `unsupported-grid-rejection`

- **문제/역할**: 조직도·패널 등의 테두리가 표 후보가 되어 독립 layout 콘텐츠를 흡수한다.
  후보가 완성된 결과를 뒤에서 지우는 대신, **cell group 직후 union 후보 승인**에서 판단한다.
- **정확한 조건**: 국소 셀 격자에 반복되는 2D 텍스트 지지 또는 허용된 완전 격자 형태가
  **없고**, 그 후보가 독립 layout 그룹들과 충돌할 때 거절한다. “2D 지지가 없으면 모두 제거”가 아니다.
- **보호 범위**: GNN owner 부재는 제거 조건이 아니다. GNN 미탐 회수를 허용한다.
  picture 포함 자체도 금지가 아니다. 하나의 picture 전체를 감싼 1행 미지지 격자는 별도로
  충돌로 취급하지만, picture의 부분영역인 raster 표는 동일하게 제거하지 않는다.
- **의존/재사용**: 생성된 셀, finder 문자, 기존 layout 그룹을 사용. bbox dedup 순서 보존.
  후단 P1·판정 캐시는 제거돼 한 번 승인한다. 별도 frame 삭제 정책과 혼동하지 않는다.
- **적용/제거**: union 내부에 항상 적용하며 공개 스위치 없음. admission hook에서 분리 가능하나
  제거 시 FP와 layout/읽기 순서 피해가 돌아올 수 있어 Table만이 아니라 VG/CF도 검사해야 한다.
- **구현/확인**: `PM:src/_table_union.py::_union_line_candidates`,
  `_union_grid_has_2d_content_support`, `_union_candidate_conflicts_with_layout`;
  교체 기록 (원문 PB:docs/benchmarks 기준 상대 경로: ../experiments/p1-shared-accepted-20260913.md).

### 4.3 정확한 선두 헤더 반복 분할 — `exact-header-split`

- **문제/역할**: 하나의 복원 격자에 같은 헤더로 시작하는 표가 반복되면 refine 단계에서 나눈다.
- **조건**: 첫 3행 안의 시그니처, 비어 있지 않은 셀 3개 이상·문자 포함 셀 2개 이상,
  공백/대소문자 정규화 후 **정확 일치**, 모든 조각 최소 4행. fuzzy 유사도 분할은 아니다.
- **입출력·비용**: 현재 격자와 텍스트 -> 행 구간별 격자. 자체 추가 TGIF 없음.
  각 조각은 기존 refine/span/header 경로로 처리한다.
- **적용/제거**: 내부 `_refine_grid_tables(..., split_repeated_headers=...)`에 제어점이 있다.
  원 finder뿐 아니라 `refine_child`도 사용하므로 **모든 진입점**에서 같은 선택을 적용해야 한다.
  공개 독립 옵션 없음. 제거하면 해당 반복표가 하나로 남는다.
- **구현/확인**: `PM:src/table.py::_refine_repeated_leading_header_cuts`,
  `_refine_grid_tables`; `PB:src/pb_table/grid_reconstruct_split.py::refine_child`;
  `tests/test_refine_execution_sharing.py`.

### 7.1 셀의 원문 참조 보존 — `table-provenance.cell-sources`

- **문제/역할**: 셀에 문자열만 남으면 어떤 원문을 썼는지 잃어 후단에서 재추정/중복한다.
  셀 생산 순간 선택한 word/character/GNN node의 실제 참조를 함께 보존한다.
- **입출력**: 기존 캐시 collection·index·좌표·scope -> `CellSource`/`source_content`.
  clone·슬라이스·연결에도 전달한다. 서로 다른 문서/페이지/부모의 같은 index는 같은 원문이 아니다.
- **경계**: 문자열 변경 후 옛 참조를 그대로 유효하게 취급하지 않는다. bbox 안에 있거나
  TGIF에 입력했다는 사실은 실제 셀 생산의 증명이 아니다.
- **적용/제거**: 정책 옵션이 아닌 생산자-소비자 데이터 계약. 외부 Text 중복 방지와
  복원 검증이 의존하므로 **단독 제거 불가**. 제거하려면 대체 원문 귀속 계약을 먼저 제공해야 한다.
- **비용/구현**: 기존 자료 참조를 전달하며 PDF 재오픈/추론 없음.
  `PM:src/_table_spans.py::SpanCell`, `PM:src/table.py`의 셀 생산;
  `LL:src/helpers/table_html/reconstruct.py`; `tests/test_cell_source_delivery.py`.

### 7.2 글꼴 높이 대신 실제 glyph로 누락 문자 수용 — `table-provenance.glyph-ownership`

- **문제/역할**: 괄호·밑줄의 실제 글자는 셀 안인데 font-height 기반 word 중심이 밖인 경우를 복구한다.
- **조건**: 기존 중심점 소유를 우선 보존한다. 놓친 glyph 전체가 유일한 셀 안에 있을 때만
  생산하고 원래 source reference를 연결한다. 여러 셀에 걸치거나 소유가 모호하면 억지 배정하지 않는다.
- **재사용**: 기존 words/RAWDICT, baseline/origin. `match_word_characters`는 본문 span
  중복 방지와 공유한다. 서로 다른 RAWDICT flags/상태의 cache를 무조건 섞지 않는다.
- **적용/제거**: 별도 스위치 없음. 셀 생산자의 glyph 보완과 출력의 glyph 소속 판정을 함께
  변경해야 한다. 한쪽만 제거하면 실제 내부 문자가 외부 Text로 새거나 검증 오류가 될 수 있다.
- **구현/확인**: `PM:src/_table_word_geometry.py`, `PM:src/_table_spans.py`;
  `tests/test_table_word_geometry.py`. 새로운 OCR 기능이 아니므로 Table 소관이다.

### 7.3 embedded font 기반 기호 문자 복구 — `table-provenance.font-symbols`

- **문제/역할**: finder에는 있지만 native word에 빠진 제어문자 기호를 실제 embedded font cmap으로
  해석해 셀에서 생산한다. 파일명/글꼴명별 추측 치환표나 임의 OCR은 쓰지 않는다.
- **입출력·비용**: 기존 finder 문자와 같은 열린 문서의 font 정보 -> 기호 문자열과 원문 참조.
  필요한 경우만 font를 읽고 xref별 cache를 사용한다.
- **적용/제거**: 공개 스위치 없음. 이 해석 부분을 제거하려면 미해석 기호의 보존/오류 계약을
  정해야 한다. 참조 검증을 끄거나 일반 Text로 우회하여 통과시켜서는 안 된다.
- **구현/확인**: `PM:src/_table_font_symbols.py`, `_table_word_geometry.py`;
  TEDS의 체크 20개·엑스 13개 복원은 승인 실측 (원문 PB:docs/benchmarks 기준 상대 경로: ../experiments/cell-source-delivery-accepted-20260917.md) 참조.
  일반적인 모든 PDF 문자 매핑 복원이 입증된 것은 아니다.

### 7.6 영역·격자·복원 출처 기록 — `table-provenance`

- **역할**: `bbox_source`, `grid_source`, `bbox_operation`, 원 GNN index, 부모/자식/복원 이력을
  구분한다. bbox가 GNN이고 grid가 find_tables인 `grid_ref`는 정상 조합이다.
- **외부/내부 구분**: public compact page JSON, 내부 TablePayload/ParsedDocument,
  분석 details는 같은 스키마가 아니다. CellSource가 있다고 `find_tables[].cell_sources`가
  공개 JSON에 전부 직렬화된다고 설명하면 안 된다.
- **적용/제거**: 진단용 상세 로그와 실제 제어 필드를 구분해야 한다. 현재 복원 그룹핑/조건은
  `source_gnn_indices`, `bbox_operation` 등에 의존하므로 provenance 전체 삭제는 행동 변경이다.
  로그만 줄이려면 제어/원문 전달 필드는 내부에 유지한다.
- **구현/확인**: `PM:src/_table_union.py`, `LL:src/helpers/document_layout.py`,
  `table_html/reconstruct.py`, ParseBench provider 전달 patch;
  `tests/test_bbox_source_recording.py`, `tests/test_restoration_handoff.py`.

## 8. 실행 기반과 최적화: 기능 정책과 별도로 판단

아래는 위 기능의 의미를 바꾸지 않고 실행 비용·중복·참조 수명을 관리하는 층이다.
“점수가 오르지 않는다”는 제거 근거가 아니다. 제거 시 의미가 같도록 대체 실행을 제공해야 한다.

- **지연 TGIF와 부모 입력 보존** (`deferred-tgif-execution`)
  - union 선택 후 필요한 영역만 resolve하며 결과 cache를 재사용한다.
    coherence 검증·실패 원복 때문에 버려질 부모도 필요시 추론한다. “최종 미채택 표는 절대 추론 안 함”은 틀리다.
  - `DeferredTGIFPipeline(deferred=False)`는 eager 비교 경로지만 승인 복원 어댑터들은
    deferred 객체/보존 입력 계약에 의존한다. 전체 stack을 그대로 두고 이 값만 바꾸는 제거는 안전하지 않다.
  - `PB:src/pb_table/deferred_tgif.py`; `tests/test_deferred_tgif.py`.
- **원본 edge 확률 전달** (`gnn-edge-evidence`)
  - 기존 GNN 결과를 전달할 뿐 새 추론이 아니다. 원 node ID 대응을 유지한다.
    node 분할을 유지하면서 이 정보를 삭제하면 입력 계약이 깨진다.
  - `PB:src/pb_table/gnn_edge_evidence.py`; `tests/test_gnn_edge_evidence.py`.
- **공용 helper/실행 경계**
  - `child_inputs`, `vg_rule_primitives`, `refine_child`, `_cells_to_rows`,
    `_collect_graphic_evidence` 등을 공유한다. 이름이 비슷하지만 계약이 다른 clustering은 억지 통합하지 않는다.
  - 이들은 옵션이 아니다. 제거가 목적이면 동일 계약 구현을 실제 소비자에 제공해야 한다.
- **같은 상태의 자료 재사용**
  - union text span, drawings, word 선택 index, placements matrix, output rows,
    grid split signals, union selection plan을 공유한다.
  - OCR/회전/flags 또는 split/stitch/내용 변경 후에도 무조건 cache를 재사용하지 않는다.
  - 관련 소스: `PM:src/table.py`, `_table_refine.py`, `_table_union.py`;
    `LL:src/helpers/table_html/reconstruct.py`; `PB:src/pb_table/material_split_rules.py`.
  - 관련 테스트: `test_drawing_sharing.py`, `test_word_search.py`, `test_grid_result_sharing.py`,
    `test_union_selection_sharing.py`, `test_refine_execution_sharing.py`.
- **헤더 실행 비용 감소**
  - HTML 경로에서 불필요한 공개 `_get_header` 호출 생략. 공개 header/Markdown/pandas 계약은 유지한다.
  - R6 입력을 기존 격자에서 직접 만들고 page 문자를 같은 상태에서 공유한다.
    교체될 부모의 R6는 지연하며 살아남는 부모·새 자식은 필요한 판정을 받는다.
  - 관련 소스: `PM:src/table.py`, `PB:src/pb_table/r6_header.py`, `r6_header_contract.py`,
    `direction_reconstruct_split.py`; `test_html_header_omission.py`, `test_r6_character_sharing.py`,
    `test_r6_direct_input.py`, `test_r6_parent_delay.py`.

현재 어댑터는 scoped process-local patch를 사용하며 같은 process에서 동시 실행하는
thread-safe 제품 API로 검증된 것이 아니다. 독립 process worker 사용 계약을 유지한다.

## 10. 선택·제거 검수 계약

1. 선택 단위는 위 기능/하위 액션으로 적는다. “V9 제거”처럼 구현 시점만 지정하지 않는다.
2. 독립 switch가 없는 항목은 먼저 **자료 전달을 유지한 행동 bypass**가 가능한지 본다.
   이 명세는 그러한 switch를 새로 구현한 문서가 아니다.
3. 삭제하는 기능의 소비자 목록을 확인한다. R6 제거 시 join/split-integrity,
   source 참조 제거 시 내부 복원 검증·외부 dedup까지 영향을 받는다.
4. 기본 계약: 좌표/원 node 대응, 실제 producer 참조, 생존 표의 R6,
   기존 내용 보존, None/empty·결측/0 구분. 기능 비활성화를 이유로 실패를 숨기지 않는다.
5. 동일 503 full 비교에서 GTRM/CON/TRM, 페이지 회귀, 실제 HTML·원문·bbox 변경을 본다.
   원문 방출/영역 선택/읽기 순서 변경이면 CF/VG/DocLayNet 관련 범위도 확인한다.
6. 비기능 refactoring/최적화만 바꾸는 경우 점수뿐 아니라 raw/normalized 출력 동등성을 요구한다.
   성능은 별도 반복 측정하며 기존 결과를 새 하드웨어 속도 보장으로 쓰지 않는다.
7. 개발 데이터에서 조정한 상수와 양식 특이 신호는 위에 공개했다. GT를 runtime에서 안 읽는다고
   overfit 가능성이 없어진 것은 아니다. 실제 제거/독립 ablation을 하지 않은 효과는 미측정이다.

## 검증 범위

제품/어댑터/OCR을 합친 승인 stack은 full-503에서 GTRM 0.8098682258124252이며,
정본과 503개 raw 출력·정규화 출력·페이지별 지표가 같았다. 이는 최종 조합 검증이며
이 저장소 단독 또는 각 중간 커밋의 독립 기여도/비회귀 검증은 아니다.
기존 실행: PB:runs/review-branches-20260917/full. 메시지·문서만 변경한 뒤
제품 소스/테스트 tree 동일성을 별도로 확인한다. 원격 push/PR은 수행하지 않는다.
전체 어댑터 시험 476 통과/6 skip, 제품 경계 16 통과, HTML 13 통과는 이전 조합의
검증 범위다. 새로운 성능·일반화 측정으로 취급하지 않는다.
