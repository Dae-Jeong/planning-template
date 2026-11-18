# __PROJECT_NAME__ Shared HTTP API Contract Baseline

최종 수정: __DATE__

FE와 BE가 공유하는 HTTP API 계약 기준선입니다. 엔드포인트가 늘어나면 도메인별 파일(예: `orders.md`, `auth.md`)로 분리하고 여기에서 링크합니다.

## 1. 공통 규칙

- **API Prefix**: `__API_PREFIX__`
- **System Probes**: `/livez`, `/readyz`, `/health`
- **성공 응답 Envelope**:
  ```json
  {
    "data": {},
    "meta": {},
    "message": null
  }
  ```
- **오류 응답 (`RFC 9457 Problem Details`)**:
  ```json
  {
    "type": "https://errors.example.com/__PROJECT_SLUG__/<error_code>",
    "title": "<human_readable_summary>",
    "status": 422,
    "detail": "<safe_public_reason>",
    "instance": "__API_PREFIX__/...",
    "errorCode": "__PROJECT_CODE__-E001"
  }
  ```
- 내부 스택 트레이스, DB 제약명, SQL 원문, 외부 vendor raw payload는 `detail`에 노출하지 않습니다.

## 2. 엔드포인트 목록

| Domain | 문서 | 요약 |
| --- | --- | --- |
| System | (예시) `/health` | Readiness / Liveness 확인 |
