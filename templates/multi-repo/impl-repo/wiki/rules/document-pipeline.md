# Document Pipeline (구현 저장소)

최종 수정: __DATE__

이 저장소는 단계 파이프라인이 아니라 **역할별 경계**를 따릅니다. **아카이빙은 중앙 기획 저장소(`__CENTRAL_REF__`)가 담당하며, 이 저장소는 최신본과 검증 증거만 관리합니다.**

## 새 문서를 만들 때 라우팅

1. 제품 기획 · 정책 · UX 계약인가? → 중앙 `__CENTRAL_REF__/planning/`에 둔다.
2. 실행 작업 단위(`__PROJECT_CODE__-WP-*` 하위 구현)와 검증 증거인가? → [`../../tasks/README.md`](../../tasks/README.md) 규칙에 따라 `tasks/`에 둔다.
3. 빠른 탐색 지도나 소유권 안내인가? → [`../_map.md`](../_map.md) 및 [`../document-ownership.md`](../document-ownership.md)에 연결한다.
4. 더 이상 유효하지 않은 구버전 문서인가? → 이 repo에 아카이브로 쌓지 않고 정리(또는 `Historical snapshot`으로 분리)한다.

## Canonical Ownership & 중복 방지

- 같은 계약이나 규칙을 이미 소유한 정본 문서가 있으면 전문을 복제하지 않고 1~2줄 요약과 링크만 둡니다.
- `wiki/` 변경 시 [`../_log.md`](../_log.md)에 날짜별 변경 내역을 남깁니다.
