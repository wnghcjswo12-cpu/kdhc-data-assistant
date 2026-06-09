# 한국지역난방공사 데이터 도우미

공공데이터포털의 한국지역난방공사 API 7종을 GPT-4o-mini가 자동 조회해
채팅으로 답하는 Streamlit 앱. (설계 배경은 [PRD.md](PRD.md) 참고)

## 설치 & 실행

```powershell
# 1) 의존성 설치
py -m pip install -r requirements.txt

# 2) .env 에 키 입력 (이미 있다면 생략)
#    GPT_API_KEY=...        OpenAI 키
#    KDHC_API_KEY=...       공공데이터포털 인증키
#    → .env 는 .gitignore 로 git 에 올라가지 않음

# 3) 실행
py -m streamlit run app.py
```

브라우저가 열리면 채팅으로 질문하면 된다. 기간을 말하지 않으면 최근 12개월 기준.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `app.py` | Streamlit 채팅 UI (세션 내 대화 유지) |
| `agent.py` | GPT-4o-mini tool-calling 루프 |
| `tools.py` | GPT에 노출할 7개 tool 스키마 + 디스패처 |
| `kdhc_api.py` | 7개 공공데이터 API 호출 계층 |
| `diagnose.py` | API 연결/파라미터 진단 도구 |

## ⚠️ 현재 상태: API 요청변수(명세) 확인 필요

엔드포인트 경로는 정상 등록되어 있으나(하위 경로는 404, 기본 경로는 응답),
표준 파라미터로 호출하면 서버가 `500 Unexpected errors` 를 반환한다.
파라미터명/날짜형식 15여 종을 바꿔도 동일해, **각 서비스의 정확한 요청변수**가
확인되면 동작한다.

### 필요한 정보 (공공데이터포털 → 마이페이지 → 해당 API → "참고문서")
각 서비스의 **요청변수 표**에서 다음을 알려주면 즉시 반영한다.
- 조회 기간 파라미터의 **정확한 영문 이름** (예: `startDate`/`endDate`, `searchStrtDe` 등)
- 날짜 **형식** (`YYYYMMDD` / `YYYY-MM-DD` / `YYYYMM`)
- 그 밖의 **필수 파라미터** 유무 (지사코드, 설비코드 등)
- (있다면) 참고문서에 적힌 **샘플 요청 URL** 한 줄

또는 참고문서의 **샘플 요청 URL**을 그대로 주면 가장 빠르다.

### 명세를 받으면 고칠 곳
[kdhc_api.py](kdhc_api.py) 상단의 `DATASET_SPEC` 한 곳만 수정하면 된다.
각 데이터셋의 `period`(파라미터명/형식)만 맞추면 전체가 동작한다.

### 진단 명령
```powershell
py diagnose.py                                   # 7개 엔드포인트 상태 확인
py diagnose.py raw fuel startDate=20240101 endDate=20241231   # 임의 파라미터 직접 시험
py diagnose.py fuel 2024 12                       # 현재 설정으로 호출
```
`raw` 모드로 명세의 샘플 파라미터가 성공하는지 확인 → 성공 조합을 `DATASET_SPEC` 에 반영.
