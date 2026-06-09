"""FastAPI 백엔드 — 키 보관 + 공사 데이터 실제 호출 + GPT 호출을 전담한다.

프론트(Streamlit)는 이 백엔드의 /chat 만 호출하며, 인증키(GPT_API_KEY,
KDHC_API_KEY)는 모두 서버 측(.env)에서만 로드되어 프론트로 노출되지 않는다.

실행:
  py -m uvicorn backend:app --reload --port 8000

엔드포인트:
  GET  /health              상태 확인
  GET  /datasets            제공 데이터셋 목록
  GET  /data/{dataset}      특정 데이터셋 직접 조회(점검/투명성용)
  POST /chat                대화 히스토리를 받아 GPT 답변 생성(도구 자동 호출)
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import agent
import kdhc_api

app = FastAPI(title="한국지역난방공사 데이터 도우미 백엔드")


# ── 요청/응답 모델 ────────────────────────────────────────────────────
class Message(BaseModel):
    role: str          # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    answer: str


# ── 엔드포인트 ────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "gpt_key_loaded": bool(agent.os.getenv("GPT_API_KEY")),
        "kdhc_key_loaded": bool(kdhc_api.KDHC_API_KEY),
    }


@app.get("/datasets")
def datasets() -> dict:
    return {
        "datasets": [
            {"key": k, "name": v["name"], "endpoint": v["endpoint"]}
            for k, v in kdhc_api.DATASET_SPEC.items()
        ]
    }


@app.get("/data/{dataset}")
def get_data(dataset: str, year: int | None = None, month: int | None = None) -> dict:
    """공사 데이터를 직접 조회한다. 인증키는 서버에서만 사용된다."""
    try:
        return kdhc_api.fetch(dataset, year=year, month=month)
    except kdhc_api.KdhcApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """대화 히스토리를 받아 GPT 답변을 생성한다.

    GPT 가 필요 시 등록된 7개 도구를 자동 호출하며, 각 도구는 서버 내부에서
    kdhc_api 를 통해 공사 데이터를 실제 호출한다.
    """
    history = [{"role": m.role, "content": m.content} for m in req.messages]
    try:
        answer = agent.run(history)
    except Exception as exc:  # 키 미설정 등
        raise HTTPException(status_code=500, detail=str(exc))
    return ChatResponse(answer=answer)
