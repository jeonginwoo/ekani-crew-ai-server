# Plan: MBTI 매칭 서비스 (4주 MVP)

## 아키텍처 개요

핵사고날 아키텍처 (Hexagonal Architecture) - 4 레이어

```
app/
├── shared/                     # 공통 VO (MBTI, Gender) - 타입 정의만, 도메인 의존성 아님
├── user/                       # 사용자 도메인 (MBTI 저장소)
├── auth/                       # 인증 도메인 (OAuth)
├── mbti_test/                  # AI MBTI 테스트 도메인 (NEW - 핵심!)
├── matching/                   # 매칭 도메인 (NEW)
├── chat/                       # 실시간 채팅 도메인 (NEW)
├── referral/                   # 레퍼럴 도메인 (NEW)
├── payment/                    # 결제 도메인 (NEW)
├── consult/                    # 상담 도메인 (기존)
└── converter/                  # 변환기 도메인 (기존)
```

### 도메인 의존성

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  MBTI Test  │ ───→ │    User     │ ←─── │  Matching   │
│  (도출)     │      │  (중심)     │      │  (매칭)     │
└─────────────┘      └─────────────┘      └─────────────┘
                           ↑
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
    │   Chat    │    │ Referral  │    │  Payment  │
    │  (대화)   │    │  (초대)   │    │  (결제)   │
    └───────────┘    └───────────┘    └───────────┘
```

- **MBTI Test** → User.mbti 업데이트 (핵심 차별점!)
- **Matching** → User.mbti 조회 (궁합/유사 매칭)
- **Chat** → User 조회 + Match 결과로 채팅방 생성
- **Referral** → User 조회 (초대자/피초대자)
- **Payment** → User 조회 (매칭권 추가)
- **MBTI Test ↔ Matching ↔ Chat**: 직접 의존 없음 (User 통해 느슨한 결합)

---

## 팀 구성 (5명 - 백엔드 집중)

> **프론트엔드**: AI로 처리 (별도 인력 불필요)

| 역할 | 인원 | 담당 | 비고 |
|------|------|------|------|
| **Team MBTI** | 2명 | mbti_test/ | |
| ↳ Person A | 1명 | 사람이 만든 질문 | 일반 질문 + 돌발 질문 |
| ↳ Person B | 1명 | AI 프롬프트 질문 | 일반 질문 + 돌발 질문 |
| **Team Match** | 2명 | | |
| ↳ Person C | 1명 | matching/ | 대기열, 매칭 로직 |
| ↳ Person D | 1명 | chat/ | 채팅방, WebSocket |
| **조장** | 1명 | 전체 서포트 | |
| ↳ Person E | 1명 | payment/, referral/ | 남는 시간에 병목 해결 |

### MBTI 테스트 (1개 페이지 - 채팅 형식)

```
┌─────────────────────────────────────────────────────────────┐
│              MBTI 테스트 (1개 페이지 - 채팅 형식)              │
├─────────────────────────────────────────────────────────────┤
│                     질문 구성 (2가지 소스)                    │
├────────────────────────────┬────────────────────────────────┤
│   Person A 담당             │   Person B 담당                │
├────────────────────────────┼────────────────────────────────┤
│ • 사람이 만든 일반 질문      │ • AI 프롬프트 일반 질문         │
│ • 사람이 만든 돌발 질문      │ • AI 프롬프트 돌발 질문         │
├────────────────────────────┴────────────────────────────────┤
│  두 타입 질문이 섞여서 채팅 테스트 구성 → MBTI 도출 → 저장     │
└─────────────────────────────────────────────────────────────┘
```

### 병렬 작업 흐름

```
[Week 1-2] MVP
Person A ───→ 사람이 만든 질문 (일반 + 돌발)
Person B ───→ AI 프롬프트 질문 (일반 + 돌발)
Person C ───→ MATCH-1 → MATCH-2 → MATCH-3
Person D ───→ CHAT-1 → CHAT-2 → CHAT-3 → CHAT-4
조장 ───────→ PAY-1 + 병목 지원

[Week 3] 매칭 고도화
Person A ───→ MATCH-4 (궁합 매칭)
Person B ───→ MATCH-5 (유사 매칭)
Person C,D ─→ TEST-1, TEST-2 (통합/부하 테스트)
조장 ───────→ PAY-2 (결제 API)

[Week 4] 그로스 해킹
Person A,B ─→ REF-1~3 (레퍼럴)
Person C,D ─→ 버그 픽스, UX 개선
조장 ───────→ 결제 테스트 + 전체 조율
```

---

## 완료된 기능 (v1.0)

> Phase 0~2 완료 - 상담소 + 변환기 기능 구현 완료

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 0 | Shared Domain (MBTI, Gender VO), User, Auth (OAuth) | ✅ |
| Phase 1 | Consult (세션, AI 인사, 메시지, SSE, 턴 관리, 분석) | ✅ |
| Phase 1 | Converter (메시지 변환, 3가지 톤, MBTI 맞춤) | ✅ |
| Phase 2 | 분석 결과 DB 저장, 히스토리 API, 마이페이지 | ✅ |

---

## 신규 Backlog (4주 MVP)

### Week 1-2: MVP 출시

> **목표**: AI MBTI 테스트로 관심 유도 + 매칭/채팅으로 가치 검증

#### 🌟 MBTI Test Domain (핵심 - Team MBTI)

##### 공통 기반 (Person A, B 협업)

- [ ] `MBTI-1` [MBTI] 채팅형 테스트 세션 기반 구조
  - **📖 유저 스토리**: "사용자로서, 채팅 형식으로 MBTI 테스트를 하고 싶다"
  - **Domain**: `MBTITestSession` (id, user_id, status, created_at)
  - **Domain**: `MBTIMessage` (role, content, question_type, source)
  - **Port**: `QuestionProviderPort` 인터페이스 (사람/AI 질문 제공)
  - **API**: `POST /mbti-test/start` → 세션 시작, 첫 질문 반환
  - **✅ 인수 조건**: 세션 생성, 질문 타입(일반/돌발) 구분

##### Person A: 사람이 만든 질문

- [ ] `MBTI-2` [MBTI] 사람이 만든 일반 질문 시스템
  - **📖 유저 스토리**: "사용자로서, 정형화된 질문에 답하고 싶다"
  - **Domain**: `HumanQuestion` (id, text, dimension, type='normal')
  - **Adapter**: `HumanQuestionProvider` - 질문 DB에서 조회
  - **✅ 인수 조건**: E/I, S/N, T/F, J/P 차원별 질문셋

- [ ] `MBTI-3` [MBTI] 사람이 만든 돌발 질문 시스템
  - **📖 유저 스토리**: "사용자로서, 예상치 못한 질문으로 깊이있는 답변을 하고 싶다"
  - **Domain**: `HumanQuestion` (id, text, dimension, type='surprise')
  - **✅ 인수 조건**: 간헐적 삽입, 정확도 향상용 질문셋

##### Person B: AI 프롬프트 질문

- [ ] `MBTI-4` [MBTI] AI 프롬프트 일반 질문 시스템
  - **📖 유저 스토리**: "사용자로서, AI가 맥락에 맞는 질문을 해주길 원한다"
  - **Adapter**: `AIQuestionProvider` (gpt-4o-mini)
  - **Prompt**: 대화 히스토리 기반 다음 질문 생성
  - **✅ 인수 조건**: 맥락 기반 후속 질문, MBTI 차원 커버

- [ ] `MBTI-5` [MBTI] AI 프롬프트 돌발 질문 시스템
  - **📖 유저 스토리**: "사용자로서, AI가 예상치 못한 질문으로 깊이 파악해주길 원한다"
  - **Prompt**: 돌발 질문 생성 프롬프트
  - **✅ 인수 조건**: 예상 못한 각도의 질문, 정확도 향상

##### 공통 결과 처리 (Person A, B 협업)

- [ ] `MBTI-6` [MBTI] 질문 응답 처리 및 대화 진행
  - **📖 유저 스토리**: "사용자로서, 질문에 답하면 다음 질문이 나온다"
  - **UseCase**: `AnswerMBTIQuestionUseCase`
  - **로직**: 사람 질문 / AI 질문 섞어서 제공
  - **API**: `POST /mbti-test/{session_id}/answer` → 다음 질문
  - **✅ 인수 조건**: 대화 히스토리 유지, 질문 타입 혼합

- [ ] `MBTI-7` [MBTI] MBTI 결과 도출 및 저장
  - **📖 유저 스토리**: "5-10턴 대화 후, MBTI 결과가 도출된다"
  - **Domain**: `MBTIResult` (mbti, confidence, analysis)
  - **UseCase**: `CalculateMBTIResultUseCase` - 응답 기반 분석
  - **API 확장**: 마지막 응답에 `is_completed: true`, `result` 포함
  - **✅ 인수 조건**: MBTI 도출, User.mbti 자동 업데이트

#### Matching Domain (Team Match)

- [ ] `MATCH-1` [Matching] 매칭 대기열 등록
  - **📖 유저 스토리**: "사용자로서, 매칭 대기열에 등록하고 싶다"
  - **Domain**: `MatchingQueue` (user_id, status, created_at)
  - **API**: `POST /matching/queue` → 대기열 등록
  - **✅ 인수 조건**: 대기열 등록, 중복 등록 방지

- [ ] `MATCH-2` [Matching] 랜덤 매칭 실행
  - **📖 유저 스토리**: "사용자로서, 대기 중인 다른 사용자와 랜덤 매칭되고 싶다"
  - **Domain**: `Match` (id, user1_id, user2_id, status, created_at)
  - **UseCase**: `RandomMatchUseCase` - 대기열에서 2명 매칭
  - **API**: `POST /matching/random` → 매칭 결과 반환
  - **✅ 인수 조건**: 2명 매칭, 매칭 시 상대 MBTI 표시, 채팅방 생성

- [ ] `MATCH-3` [Matching] 일일 매칭 횟수 제한
  - **📖 유저 스토리**: "무료 사용자로서, 하루 3회까지 매칭할 수 있다"
  - **Domain 확장**: `User.daily_match_count`, `User.last_match_date`
  - **UseCase 확장**: 매칭 전 횟수 체크
  - **API 확장**: 잔여 횟수 반환, 초과 시 402 에러
  - **✅ 인수 조건**: 3회 초과 시 에러, 자정에 리셋

#### Chat Domain (Team Match)

- [ ] `CHAT-1` [Chat] 채팅방 생성
  - **📖 유저 스토리**: "매칭 성공 시, 자동으로 채팅방이 생성된다"
  - **Domain**: `ChatRoom` (id, match_id, created_at)
  - **Domain**: `ChatMessage` (id, room_id, sender_id, content, created_at)
  - **Repository**: `ChatRoomRepository`
  - **✅ 인수 조건**: 매칭 시 채팅방 자동 생성

- [ ] `CHAT-2` [Chat] WebSocket 연결
  - **📖 유저 스토리**: "사용자로서, 실시간으로 메시지를 주고받고 싶다"
  - **Adapter**: WebSocket 핸들러 (FastAPI WebSocket)
  - **API**: `WS /chat/{room_id}`
  - **✅ 인수 조건**: WebSocket 연결, 실시간 메시지 송수신

- [ ] `CHAT-3` [Chat] 메시지 저장 및 조회
  - **📖 유저 스토리**: "사용자로서, 이전 메시지를 다시 볼 수 있다"
  - **Repository**: `ChatMessageRepository`
  - **API**: `GET /chat/{room_id}/messages` → 메시지 히스토리
  - **✅ 인수 조건**: 메시지 영속화, 페이지네이션

- [ ] `CHAT-4` [Chat] 채팅방 목록 조회
  - **📖 유저 스토리**: "사용자로서, 내 채팅방 목록을 보고 싶다"
  - **API**: `GET /chat/rooms` → 내 채팅방 목록
  - **✅ 인수 조건**: 최근 메시지 미리보기, 안 읽은 메시지 카운트

---

### Week 3: 매칭 고도화

> **목표**: MBTI 기반 매칭 알고리즘으로 매칭 품질 개선

#### MBTI 기반 매칭 알고리즘 (Team MBTI)

- [ ] `MATCH-4` [Matching] MBTI 궁합 매칭
  - **📖 유저 스토리**: "사용자로서, MBTI 궁합이 좋은 사람과 매칭되고 싶다"
  - **Domain**: `MBTICompatibility` - 궁합 점수 계산
  - **UseCase**: `CompatibilityMatchUseCase` - 궁합 기반 매칭
  - **API**: `POST /matching/compatibility` → MBTI 궁합 매칭
  - **✅ 인수 조건**: 궁합 점수 높은 순 매칭

- [ ] `MATCH-5` [Matching] 유사 MBTI 매칭
  - **📖 유저 스토리**: "사용자로서, 나와 비슷한 MBTI 사람과 매칭되고 싶다"
  - **UseCase**: `SimilarMBTIMatchUseCase`
  - **API**: `POST /matching/similar` → 유사 MBTI 매칭
  - **✅ 인수 조건**: 같은/유사 MBTI 우선 매칭

---

### Week 4: 그로스 해킹

> **목표**: 서비스가 스스로 확산되고, 누군가는 실제로 돈을 지불하는지 검증

#### Referral Domain (레퍼럴)

- [ ] `REF-1` [Referral] 초대 코드 생성
  - **📖 유저 스토리**: "사용자로서, 친구 초대용 코드를 받고 싶다"
  - **Domain**: `ReferralCode` (code, user_id, created_at)
  - **API**: `GET /referral/code` → 내 초대 코드
  - **✅ 인수 조건**: 유니크 코드 생성, 사용자당 1개

- [ ] `REF-2` [Referral] 초대 코드 사용
  - **📖 유저 스토리**: "신규 사용자로서, 초대 코드를 입력하면 보상을 받는다"
  - **Domain**: `ReferralReward` (referrer_id, referee_id, rewarded_at)
  - **UseCase**: `UseReferralCodeUseCase`
  - **API**: `POST /referral/use` → 코드 사용
  - **✅ 인수 조건**: 양쪽에 추가 매칭권 +1, 중복 사용 방지

- [ ] `REF-3` [Referral] 레퍼럴 현황 조회
  - **📖 유저 스토리**: "사용자로서, 내가 초대한 친구 수를 보고 싶다"
  - **API**: `GET /referral/stats` → 초대 현황
  - **✅ 인수 조건**: 초대 수, 보상 내역

#### Payment (최소 결제)

- [ ] `PAY-1` [Payment] 매칭권 구매
  - **📖 유저 스토리**: "사용자로서, 추가 매칭권을 구매하고 싶다"
  - **Domain**: `MatchingTicket` (user_id, count, purchased_at)
  - **UseCase**: `PurchaseTicketUseCase`
  - **API**: `POST /payment/ticket` → 매칭권 구매
  - **✅ 인수 조건**: 1,000원/회 결제, 매칭권 추가

- [ ] `PAY-2` [Payment] 결제 연동 (토스페이먼츠 or 카카오페이)
  - **📖 유저 스토리**: "사용자로서, 간편하게 결제하고 싶다"
  - **Adapter**: 결제 API 연동
  - **✅ 인수 조건**: 실결제 처리, 결제 내역 저장

---

## 성공 지표 체크리스트

| KR | 목표 | 측정 방법 |
|----|------|----------|
| 가입자 | 100명 | User 테이블 count |
| 레퍼럴 유입 | 20명+ | ReferralReward 테이블 count |
| WAU | 20명+ | 주간 로그인 유저 |
| 대화 지속률 | 50%+ | 매칭 후 5개 이상 메시지 교환 비율 |
| 결제 유저 | 1명+ | Payment 테이블 count |