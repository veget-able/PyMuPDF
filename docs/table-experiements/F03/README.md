# F03: Thin filled rectangles and painted vector strokes

Status: specification draft. No runtime implementation or benchmark result is included in this commit.

Branch: table-experiements/f03-vector-rule-recovery

Base: pymupdf main at 1d34e04da00b7673a0b2c3f68b5a5246793a50b8.

## Scope and execution boundary

- PM table.py의 실제 도형→edge 변환과 기존 drawing cache 소비.
- raster와 분리 가능하므로 현 구분 유지함. 추가 drawing 추출 없음.
- 필수 기반: main의 finder 및 필요한 F02 입력 계약만 명시함.

## Dependencies

The following are proposed dependencies, not merged or independently validated revisions. Only necessary contracts are reused; unrelated policies must not be imported.

- No additional feature dependency is currently proposed; compatibility with main still requires validation.

## Validation and page-level attribution

Follow [the evaluation contract](../evaluation-contract.json). For the initial implementation, compare against the same main and pinned prerequisite combination. For later changes, compare against this feature’s previous validated revision with identical dependencies.

List every improved and regressed page, score-neutral output change, and per-metric regression. Keep TP loss/recovery identities, bbox/cell/header changes, original-source ownership and text output evidence. A positive aggregate or preserved table count does not prove preservation. No page improvement or regression has been measured for this draft.

## Continued development

Add implementation, wiring, tests and updated evidence in subsequent commits on this branch. Record compatibility pairs for cross-repository changes. Merge prerequisite updates explicitly and measure their effect separately. The working revision may be newer than the validated revision; do not report unmeasured work as validated. Do not create product feature flags merely to stage the port.

The [branch index](../README.md) links the related feature drafts. Existing production branches remain unchanged.
