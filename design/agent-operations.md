# 에이전트 실전 운용 플레이북 (v1.1)

이 문서는 `lets_talk` 실전 운용에서 검증된 장점을 살리고, 당시 발생했던 3가지 마찰(**수동 보드 불일치 · 검증 큐 적체 · 앞단 스펙 노후화**)을 구조적으로 제거한 표준 운용 규약입니다.

---

## 1. Single Writer + Auto-Sync (`30-work.md` 수동 표 편집 금지)

- 각 WP의 메타(`Phase`, `Status`, `Owner`, `Covers SPEC`, `Blocker`, `Human Check`, `Reusable Insight`)는 **`30-work/work-NNN-*.md` 파일 1곳만** 수정합니다.
- `30-work.md`의 4개 `AUTO` 블록(`HUMAN_QUEUE`, `WP_BOARD`, `SPEC_COVERAGE`, `OPEN_MIRROR`)은 `sync_planning.py`가 자동 생성합니다.
- 미착수 기능은 `30-work.md`의 `신규 기능 로드맵` 표에 1줄로만 걸어두고, 착수하여 `work-NNN-*.md` 파일을 생성하는 순간 로드맵 표에서 제거합니다(`check_planning.py`가 중복 잔존 차단).

---

## 2. 2커밋 실행 & 회수 사이클

1. **1단계 (`plan: WP-NNN ...`)**:
   - `work-NNN-*.md` 작성 (`Scope In/Out`, `Domain/Contract`, `Human Check`, `REQ-*` 표, `Release Gate`).
   - `30-work.md` 로드맵 표에서 해당 행을 제거하고 `sync_planning.py` 실행.
2. **2단계 (`WP-NNN ...`)**:
   - TDD 구현 + `Log / DB / FE` 1차 증거 확보 후 기술 Release Gate `[x]` 체크.
   - `Status`를 `agent_verified` 또는 `awaiting_human`으로 갱신 → `sync_planning.py` 실행 → `planning/log.md` 회수 기록 추가 → `check_planning.py` 통과 확인.

---

## 3. 2트랙 검증 게이트 (`agent_verified` vs `awaiting_human`)

사람 승인 큐가 마비되지 않도록 검증 완료 상태를 `Human Check:` 유무에 따라 2갈래로 나눕니다:

```text
draft ──▶ in_dev ──┬── (Human Check: none + 기술 Gate [x]) ──▶ agent_verified ──(--accept-verified)──▶ done
                   │
                   └── (Human Check: <1줄> + 기술 Gate [x]) ─▶ awaiting_human ──(--accept WP-ID)────▶ done
```

- **`agent_verified`**: 백엔드·DB·리팩터링·자동 E2E로 검증이 완결돼 사람 눈 확인이 불필요한 WP. 사람 큐를 점유하지 않으며 배포/Phase 컷 때 `sync_planning.py --accept-verified` 1줄로 일괄 `done` 마감합니다.
- **`awaiting_human`**: 레이아웃 감성, 모바일 뷰포트, OS 알림, 실단말 등 사람이 직접 봐야 할 항목이 있는 WP. `30-work.md` 최상단 `Human Sign-off Queue` 표에 확인 1줄만 자동 추출되며, 사람이 확인 후 `sync_planning.py --accept <WP-ID>`로 닫습니다.
- **`qa_blocked`**: 결함(`FAIL`) 또는 환경 제약(`UNKNOWN`)으로 정지된 상태. 반드시 `Blocker:`에 구체적 해소 조건을 적습니다.

---

## 4. Red Line 기반 정책 위임 (`policy-direction.md`)

- **위임(에이전트 확정 후 근거 기록)**: 서비스 전제와 기본 스탠스 안에서 세부 정책 변수·문구·정렬 디테일 결정.
- **6대 Red Line (사람 전용 — 에이전트 단독 확정 금지)**:
  1. 제품 Scope 변경 (v1 In/Out 추가·삭제)
  2. 인증 · 보안 · 권한 모델 변경
  3. 데이터 영구 삭제 · 보존 기한 · 백업 정책
  4. 외부 노출 (공개 가입, 비인증 공유 링크 등)
  5. 비용 발생 선택 (유료 API, 관리형 클라우드 서비스)
  6. 미결 `OPEN-*` 결정의 임의 확정

> **`OPEN-*` 역추적 차단**: `10-decision.md`에서 `OPEN-NNN`이 `DEC`로 확정되어 미결 표에서 빠지면, `20-spec*`나 `30-work*`에 남아 있던 `OPEN-NNN` 문구도 즉시 갱신해야 합니다(`check_planning.py`가 `stale-open-reference`로 자동 검출).

---

## 5. 성공 판단 3종 1차 증거 & 근거 라벨

Build / Typecheck / Unit Test 통과는 전제일 뿐입니다. 보고 시 `Source / Code / Tool / Inference / Unknown` 라벨을 구분하고 다음 3종 증거를 남깁니다:
1. **Log**: 기대 처리 흐름 완료 로그 및 에러/경고 부재
2. **DB 정합성**: 실제 저장 row, 상태 전이, tombstone, 멱등성 중복 0건
3. **FE 동작 (+ Network negative)**: 화면 동작 및 발생하지 말아야 할 요청의 미전송 확인

---

## 6. 정기 5-WP 디자인 패턴 리뷰 & 3단계 QA Sweep & 교훈 증류(`--distill`)

- **5-WP 패턴 리뷰**: `log.md`의 `리뷰 기준 WP: PROJ-WP-NNN` 이후 5개 이상 WP가 검증 완료되면 `check_planning.py`가 `pattern-review-due` 경고를 띄웁니다. `git diff`로 DDD/레이어/추상화 드리프트를 점검하고 `log.md`의 `리뷰 기준 WP:`를 최신 번호로 올립니다.
- **3단계 QA Sweep (`templates/qa-sweep.md`)**: 기능 묶음 완료 시 ① 기능별 QA → ② 통합 시나리오 E2E → ③ Adversarial 공격표면 점검으로 실배포 결함을 텁니다.
- **교훈 증류 (`--distill`)**: 범용 트러블슈팅 인사이트가 나온 WP에만 `Reusable Insight: <1줄>`을 적어두고, Phase 종료 시 `sync_planning.py --distill`로 모아 `40-architecture/`, `policy-qa-checklist.md`, 또는 중앙 기술 위키로 승격합니다.
