# F05: Independent table admission

Status: specification draft. No runtime implementation or benchmark result is included in this commit.

Branch: table-experiements/f05-table-admission

Base: pymupdf main at 1d34e04da00b7673a0b2c3f68b5a5246793a50b8.

## Scope and execution boundary

- PM _table_append_context/_table_append_structure/_table_component_context 및 union append 소비 위치.
- 지연 승인·공유 glyph 색인·정상 양식 보호까지 현재 채택된 계약을 함께 포함함.
- 독립 표 추가 권한만 제약하고 supply/grid_ref/split의 의미를 바꾸지 않음.
- 필수 기반: F02, F01의 원문/재료 참조 중 실제 소비 부분.

## Dependencies

The following are proposed dependencies, not merged or independently validated revisions. Only necessary contracts are reused; unrelated policies must not be imported.

- F02: table-experiements/f02-ruling-gnn-union (revision pending).
- F01: table-experiements/f01-cell-source-output (revision pending).

## Validation and page-level attribution

Follow [the evaluation contract](../evaluation-contract.json). For the initial implementation, compare against the same main and pinned prerequisite combination. For later changes, compare against this feature’s previous validated revision with identical dependencies.

List every improved and regressed page, score-neutral output change, and per-metric regression. Keep TP loss/recovery identities, bbox/cell/header changes, original-source ownership and text output evidence. A positive aggregate or preserved table count does not prove preservation. No page improvement or regression has been measured for this draft.

## Continued development

Add implementation, wiring, tests and updated evidence in subsequent commits on this branch. Record compatibility pairs for cross-repository changes. Merge prerequisite updates explicitly and measure their effect separately. The working revision may be newer than the validated revision; do not report unmeasured work as validated. Do not create product feature flags merely to stage the port.

The [branch index](../README.md) links the related feature drafts. Existing production branches remain unchanged.
