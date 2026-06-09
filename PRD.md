# PRD — 한국지역난방공사 데이터 도우미

## 1. 개요

한국지역난방공사 설비 운영·관리 담당자를 위한 **대화형 데이터 도우미**.
사용자가 채팅으로 공사 데이터를 물어보면, AI가 공공데이터포털의 한국지역난방공사 API 7종을 **자동으로 선택·조합 호출**하여 답변한다. 대화 맥락은 **세션 내에서 기억(Memory)** 되어 이어서 질문할 수 있다.

### 목표
- 자연어 질문만으로 공사 운영 데이터(연료·발전·전기판매·열판매·열생산·에너지·기상)를 조회한다.
- AI가 필요한 API를 스스로 판단해 도구(Tool)로 호출하고, 여러 데이터를 결합해 답한다.
- 직전 대화를 기억하여 후속 질문에 맥락을 이어 답한다.
- 결과를 표 중심으로 명확하게 제시한다.

### 비목표 (현 단계 제외)
- 사용자 인증/권한 관리
- 영구 데이터베이스 저장 (세션 종료 시 대화는 사라짐)
- 다중 사용자 동시 운영, 배포 인프라

---

## 2. 사용자 및 사용 시나리오

- **사용자**: 한국지역난방공사 설비 운영 및 관리 담당자
- **예시 질문**
  - "최근 1년간 연료 사용량 추이를 보여줘"
  - "지난달 발전소 생산실적과 전기 판매량을 비교해줘"
  - "기온이 낮을 때 열 생산량이 어떻게 변했어?"
  - "에너지 사용량과 연료 사용량을 함께 정리해줘"
  - (후속) "그럼 작년 같은 기간은 어땠어?" ← **Memory로 직전 맥락을 이어받음**

---

## 3. 확정 설계 사항 (인터뷰 결과)

| 항목 | 결정 |
|---|---|
| 언어/런타임 | Python |
| UI | Streamlit 채팅 (얇은 프론트엔드) |
| 백엔드 | FastAPI (키 보관 · 데이터 호출 · GPT 호출 전담) |
| LLM | OpenAI GPT-4o-mini (Tool/Function calling) |
| 대화 기억(Memory) | 세션 내 유지 (프론트 `session_state` ↔ 백엔드 `/chat` 전달) |
| API 규격 | data.go.kr 표준 파라미터로 우선 구현 후 실행하며 보정 |
| 답변 표현 | 표(테이블) 중심 + 자연어 요약 |
| OpenAI 키 | `.env`의 `GPT_API_KEY` (백엔드에서만 로드) |
| 공사 API 키 | `.env`의 `KDHC_API_KEY` (백엔드에서만 로드) |
| 기본 조회 기간 | 기간 미지정 시 최근 12개월 |

---

## 4. 시스템 구성 (프론트/백엔드 분리)

키와 데이터 호출을 프론트에서 분리하기 위해 **2-티어**로 구성한다.

```
[브라우저] ─ Streamlit(app.py) ──HTTP──▶ FastAPI(backend.py) ─┬─▶ OpenAI GPT-4o-mini
  채팅 UI      얇은 클라이언트                키/오케스트레이션   │     (도구 자동 호출)
  대화 기억    (키를 모름)                                      └─▶ 한국지역난방공사 API 7종
```

- **프론트(app.py)**: 인증키를 다루지 않는다. 대화 히스토리를 백엔드 `/chat` 으로 보내 답변만 받아 표시한다. 대화 기억은 `st.session_state` 가 보관한다.
- **백엔드(backend.py)**: `GPT_API_KEY`/`KDHC_API_KEY` 를 서버 측 `.env` 에서만 로드한다. GPT 호출과 공사 데이터 실제 호출을 전담하여 키가 프론트로 노출되지 않는다.

### 백엔드 엔드포인트
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/health` | 상태 및 키 로드 여부 확인 |
| GET | `/datasets` | 제공 데이터셋 목록 |
| GET | `/data/{dataset}` | 특정 데이터셋 직접 조회(점검/투명성용) |
| POST | `/chat` | 대화 히스토리를 받아 GPT 답변 생성(도구 자동 호출) |

---

## 5. 대화 기억 기능 (Memory)

### 5.1 정의 및 범위
- **세션 메모리**: 한 번의 사용 세션 동안 사용자·AI의 모든 발화를 순서대로 보관한다.
- 보관 위치: 프론트의 `st.session_state.history` (role/content 목록).
- 매 질문마다 **전체 히스토리**를 백엔드 `/chat` 으로 전송하여, GPT가 직전 맥락을 반영해 답하도록 한다.

### 5.2 동작
1. 사용자가 메시지를 입력 → `history` 에 `{"role":"user", ...}` 추가.
2. 프론트가 `history` 전체를 `/chat` 으로 POST.
3. 백엔드가 시스템 프롬프트 + 히스토리를 GPT 메시지로 구성(`agent.build_messages`)하여 호출.
4. 응답을 `history` 에 `{"role":"assistant", ...}` 로 추가하고 화면에 렌더링.

### 5.3 정책
- **유지 범위**: 세션 내에서만. 브라우저 새로고침/종료 시 초기화된다(영구 저장 안 함).
- **초기화**: 사이드바의 "대화 초기화" 버튼으로 `history` 를 비운다.
- **후속 질문**: "그럼 작년은?", "거기에 기온도 추가해줘" 같은 맥락 의존 질문을 지원한다.

---

## 6. 데이터 조회 도구 (Tool) 목록

GPT-4o-mini에 **데이터셋별로 분리된 7개 도구**를 노출한다(`tools.py`). 분리함으로써 GPT가 질문에 맞는 도구를 정확히 선택하고, 필요하면 여러 도구를 **조합 호출**한다.

| # | Tool 이름 | 설명 | 데이터셋 키 | End Point |
|---|---|---|---|---|
| 1 | `get_fuel_usage` | 연료사용량(발전·열생산에 쓰인 연료량) 조회 | `fuel` | `https://apis.data.go.kr/B550373/kdhcFuel` |
| 2 | `get_power_production` | 발전소 생산실적(발전량) 조회 | `power_prod` | `https://apis.data.go.kr/B550373/kdhcPwrProd` |
| 3 | `get_power_sell` | 전기판매량(GW) 조회 | `power_sell` | `https://apis.data.go.kr/B550373/kdhcPowerSell` |
| 4 | `get_heat_sell` | 지역난방 열판매량 조회 | `heat_sell` | `https://apis.data.go.kr/B550373/kdhcHeatSell` |
| 5 | `get_heat_production` | 열생산량(GW) 조회 | `heat_prod` | `https://apis.data.go.kr/B550373/kdhcHeatProd` |
| 6 | `get_energy_usage` | 에너지사용량 조회 | `energy` | `https://apis.data.go.kr/B550373/kdhcEnergy` |
| 7 | `get_weather_observation` | 기상관측정보(기온 등) 조회 — 수요·생산과 날씨 비교용 | `weather` | `https://apis.data.go.kr/B550373/kdhcWeatherObser` |

### 6.1 도구 공통 입력 파라미터
| 파라미터 | 타입 | 설명 |
|---|---|---|
| `year` | integer (선택) | 조회 연도(예: 2025). 생략 시 최근 12개월. |
| `month` | integer (선택, 1~12) | 조회 월. 생략 가능. |

- 사용자가 기간을 명시하지 않으면 GPT는 `year`/`month` 를 비워 호출하고, 백엔드(`kdhc_api`)가 **최근 12개월** 범위로 조회한다.
- 인증키(`KDHC_API_KEY`)는 도구 실행 시 **백엔드에서만** `serviceKey` 로 사용되며 코드/프론트에 노출되지 않는다.

### 6.2 도구 호출 흐름
1. `/chat` 이 GPT를 호출하면서 7개 도구 스키마를 함께 전달(`tool_choice="auto"`).
2. GPT가 필요한 도구를 선택해 호출 → 백엔드가 `tools.dispatch` 로 `kdhc_api.fetch` 실행.
3. 결과(JSON)를 도구 메시지로 GPT에 회신, GPT가 종합해 최종 답변 생성.
4. 도구 호출은 최대 라운드 수(`agent.MAX_TOOL_ROUNDS`)로 제한해 무한 루프를 방지한다.

---

## 7. 기능 요구사항

### F1. 채팅 인터페이스 (프론트)
- Streamlit 채팅 UI. 대화 히스토리를 화면에 표시하고 `session_state` 로 유지.
- 사이드바: 예시 질문, 백엔드 연결/키 로드 상태 표시, 대화 초기화 버튼.

### F2. AI 자동 도구 호출 (백엔드)
- GPT-4o-mini가 7개 도구 중 질문에 필요한 것을 자동 선택·조합 호출한다.
- 호출 결과를 종합해 최종 답변을 생성한다.

### F3. API 조회 계층 (`kdhc_api.py`)
- 각 도구는 해당 End Point를 `KDHC_API_KEY` 로 호출한다.
- 기간 미지정 시 최근 12개월을 기본 범위로 사용한다.
- 응답을 파싱해 구조화된 결과로 반환한다.

### F4. 답변 표현
- 결과를 표(마크다운 테이블)로 정리하고 자연어 요약을 덧붙인다. 출처(데이터셋)를 밝힌다.

### F5. 세션 대화 기억 (Memory) — 5장 참조
- 직전 대화 맥락을 기억하여 후속 질문에 이어 답한다.

---

## 8. 비기능 요구사항

- **보안(키 분리)**: 모든 키는 백엔드 `.env` 에서만 로드. 프론트는 키를 알지 못한다. `.env` 는 `.gitignore` 에 포함하여 git에 올리지 않으며, `.env.example` 에는 키 이름만 둔다.
- **견고성**: API 응답이 없거나 오류일 때, 백엔드는 적절한 HTTP 오류로, 프론트는 사용자에게 상황을 안내한다. 추측으로 답하지 않는다.
- **확장성**: 도구를 데이터셋별로 분리하고, API 규격은 `kdhc_api.DATASET_SPEC` 한 곳에서 조정하도록 하여 향후 추가/수정이 쉽다.

---

## 9. 파일 구성

```
session 13/
├── PRD.md              # 본 문서
├── README.md           # 설치/실행/현황
├── .env                # GPT_API_KEY, KDHC_API_KEY  (실제 키, git 제외)
├── .env.example        # 키 이름만 있는 템플릿
├── .gitignore          # .env, __pycache__ 등 제외
├── requirements.txt    # streamlit, openai, requests, python-dotenv, pandas, fastapi, uvicorn
├── app.py              # [프론트] Streamlit 채팅 UI (세션 메모리, 백엔드 호출)
├── backend.py          # [백엔드] FastAPI (키 보관·데이터 호출·GPT 호출)
├── agent.py            # GPT-4o-mini tool-calling 루프 (시스템 프롬프트·메시지 구성)
├── tools.py            # GPT에 노출할 7개 도구 스키마 + 디스패처
├── kdhc_api.py         # 7개 공공데이터 API 호출 계층 (DATASET_SPEC)
└── diagnose.py         # API 연결/파라미터 진단 도구
```

---

## 10. 동작 흐름 (종합)

1. 사용자가 채팅 입력 → 프론트가 대화 히스토리(Memory) 전체를 백엔드 `/chat` 으로 전송.
2. 백엔드가 GPT-4o-mini 호출 → GPT가 7개 도구 중 필요한 것을 자동 선택·조합 호출.
3. 각 도구가 `kdhc_api` 를 통해 해당 End Point를 `KDHC_API_KEY` 로 조회(기간 미지정 시 최근 12개월).
4. GPT가 결과를 종합 → 표 + 자연어 요약으로 답변.
5. 프론트가 답변을 화면에 표시하고 히스토리에 추가 → 후속 질문에 맥락 반영.

---

## 11. 실행 방법

```powershell
# 의존성 설치
py -m pip install -r requirements.txt

# 1) 백엔드 실행
py -m uvicorn backend:app --port 8000

# 2) 프론트 실행 (다른 터미널)
py -m streamlit run app.py
```

---

## 12. API 호출 표준 가정 (실행하며 보정)

각 API에 대해 다음 표준 규격을 가정하고 우선 구현했다. 실제 응답이 다르면 `kdhc_api.DATASET_SPEC` 의 `period`(파라미터명/날짜형식)만 조정한다.

- **요청 파라미터**: `serviceKey`, `pageNo`, `numOfRows`, `type`(json), 조회 기간(시작/종료)
- **응답 구조**: `response.body.items` 하위에 레코드 목록

---

## 13. 현황 및 리스크

- **API 요청변수 확인 필요**: 표준 파라미터로 호출 시 7개 엔드포인트 모두 `500 Unexpected errors` 를 반환한다. 경로는 정상(하위 경로는 404)이나, 파라미터를 여러 형태로 바꿔도 동일하다. 각 서비스 "참고문서"의 정확한 요청변수가 확인되면 `DATASET_SPEC` 수정만으로 동작한다.
- **인증키 형식 확인**: 현재 `KDHC_API_KEY` 가 64자리 16진수로, 일반적 data.go.kr 인증키(80자 이상 Base64) 형태와 달라 활성화/형식 확인이 필요할 수 있다.
- 활용신청 승인·활성화가 7개 서비스 모두에 적용되어 있어야 한다.

---

## 14. 향후 확장 (선택)

- 차트(추이 그래프) 시각화 추가
- 데이터/대화 영구 저장(현재는 세션 메모리)
- 출처(어느 API에서 온 값인지) 표기 강화
- 백엔드 인증/배포 구성
