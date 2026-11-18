# Obsidian 오케스트레이션 연동 가이드 (`__PROJECT_NAME__`)

이 문서는 `__PROJECT_NAME__`(`__PROJECT_SLUG__`)가 중앙 Obsidian 볼트 오케스트레이션(`harness`, `scheduler`, `project-orchestrator`)과 함께 운영될 때 **이중 정본(Dual-SSOT)을 방지**하기 위한 소유권 규칙입니다.

## 소유권 매트릭스

| 영역 | 단일 정본 소유자 | 설명 |
| --- | --- | --- |
| 활성 작업 할당 · 세션 바인딩 · 최종 수락 상태 | `Obsidian/wiki/projects/__PROJECT_SLUG__/tasks/` | 오케스트레이터와 세션 인계의 실행 정본 |
| 제품 결정 (`DEC`/`OPEN`), 계약 (`20-spec/`), WP 설계·`REQ-*` (`30-work/`) | 이 저장소의 `planning/` | 제품 코드와 함께 버전 관리되는 설계·계약 정본 |
| `planning/30-work.md` | 이 저장소 (WP 카탈로그 & 커버리지 뷰) | 독립 실행 보드로 쓰지 않고 Obsidian Task ID 링크 및 Spec Coverage 확인용으로 유지 |
| 변경 이력 | 목적 분리 | `planning/log.md` = 제품 WP/컷 마일스톤 · `Obsidian/wiki/log/` = 문서 스냅샷·세션 작업 기록 |
