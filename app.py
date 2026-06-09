"""Streamlit 채팅 UI — 한국지역난방공사 데이터 도우미 (프론트엔드).

이 화면은 얇은 클라이언트다. 인증키를 직접 다루지 않으며, 대화 히스토리를
백엔드(/chat)로 보내 답변만 받아 표시한다. 키 보관·공사 데이터 실제 호출·
GPT 호출은 모두 백엔드(backend.py)가 담당한다.

실행:
  1) 백엔드:  py -m uvicorn backend:app --port 8000
  2) 프론트:  py -m streamlit run app.py

대화는 세션 내에서만 유지된다(st.session_state).
"""

from __future__ import annotations

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="한국지역난방공사 데이터 도우미", page_icon="🔥")

st.title("🔥 한국지역난방공사 데이터 도우미")
st.caption(
    "공공데이터포털 API 7종(연료·발전·전기판매·열판매·열생산·에너지·기상)을 "
    "백엔드가 자동 조회해 답합니다. 기간을 말하지 않으면 최근 12개월 기준입니다."
)

# 세션 내 대화 기억
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("예시 질문")
    st.markdown(
        "- 최근 1년 연료 사용량 추이 보여줘\n"
        "- 지난달 발전량과 전기판매량 비교해줘\n"
        "- 기온과 열생산량 관계를 정리해줘\n"
        "- 에너지사용량과 연료사용량 함께 표로"
    )
    st.divider()
    st.caption(f"백엔드: {BACKEND_URL}")
    # 백엔드 상태 표시
    try:
        h = requests.get(f"{BACKEND_URL}/health", timeout=3).json()
        st.success("백엔드 연결됨")
        st.caption(
            f"GPT 키: {'✅' if h.get('gpt_key_loaded') else '❌'} / "
            f"공사 키: {'✅' if h.get('kdhc_key_loaded') else '❌'}"
        )
    except Exception:
        st.error("백엔드에 연결할 수 없습니다. uvicorn 이 실행 중인지 확인하세요.")
    if st.button("대화 초기화"):
        st.session_state.history = []
        st.rerun()


def ask_backend(history: list[dict[str, str]]) -> str:
    """대화 히스토리를 백엔드 /chat 에 보내 답변을 받는다."""
    resp = requests.post(
        f"{BACKEND_URL}/chat",
        json={"messages": history},
        timeout=120,
    )
    if resp.status_code != 200:
        detail = resp.json().get("detail", resp.text) if resp.content else resp.text
        raise RuntimeError(f"백엔드 오류({resp.status_code}): {detail}")
    return resp.json()["answer"]


# 기존 대화 렌더링
for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

# 입력 처리
prompt = st.chat_input("공사 데이터에 대해 물어보세요")
if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("백엔드가 데이터를 조회하고 정리하는 중..."):
            try:
                answer = ask_backend(st.session_state.history)
            except Exception as exc:
                answer = f"⚠️ 오류가 발생했습니다: {exc}"
        st.markdown(answer)

    st.session_state.history.append({"role": "assistant", "content": answer})
