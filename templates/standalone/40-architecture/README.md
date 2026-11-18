# __PROJECT_NAME__ Architecture Invariants

최종 수정: __DATE__

여러 SPEC/WP가 **공통으로 공유하는 장기 도메인 불변식(invariant), 상태 머신, 경계 계약**만 승격해 기록합니다.

## 승격 기준

다음 중 하나에 해당할 때만 `40-architecture/<topic>.md` 문서를 생성합니다:
- 2개 이상 SPEC/WP가 같은 Aggregate 경계 또는 불변식을 공유함
- 동일한 상태 머신이나 원장(ledger) 규칙이 반복됨
- API status, FE UI state, DB guard, QA evidence가 같은 상태값을 참조함

## 문서 목록

- (아직 승격된 공통 아키텍처 문서가 없습니다 — 발생 시 추가하고 여기와 `SPEC`/`WP`에서 링크하세요.)
