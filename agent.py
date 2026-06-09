"""OpenAI GPT-4o-mini tool-calling 루프.

대화 메시지 리스트(messages)를 받아, 필요한 tool 을 자동 호출하고
최종 답변 텍스트를 생성한다. 대화 기억은 호출 측(Streamlit session_state)이 유지한다.
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

import tools

load_dotenv()

MODEL = "gpt-4o-mini"
MAX_TOOL_ROUNDS = 6  # tool 호출 무한루프 방지

SYSTEM_PROMPT = (
    "너는 한국지역난방공사 설비 운영·관리 담당자를 돕는 데이터 도우미다. "
    "사용자 질문에 답하기 위해 제공된 tool 들로 공사 공공데이터를 직접 조회한다. "
    "여러 데이터가 필요하면 여러 tool 을 조합해 호출하라. "
    "사용자가 기간을 명시하지 않으면 최근 12개월 기준으로 답한다(tool 의 year/month 를 비워 호출). "
    "답변은 한국어로 하고, 핵심 수치는 표(마크다운 테이블)로 정리한 뒤 간단한 자연어 요약을 덧붙인다. "
    "어떤 데이터셋에서 가져온 값인지 출처를 밝혀라. "
    "데이터가 없거나 조회에 실패하면 추측하지 말고 그 사실과 가능한 원인을 설명하라."
)


def _client() -> OpenAI:
    api_key = os.getenv("GPT_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GPT_API_KEY 가 설정되지 않았습니다. .env 파일에 OpenAI 키를 입력하세요."
        )
    return OpenAI(api_key=api_key)


def build_messages(history: list[dict[str, str]]) -> list[dict[str, Any]]:
    """시스템 프롬프트 + 대화 히스토리를 OpenAI 메시지 형식으로 만든다."""
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    return messages


def run(history: list[dict[str, str]]) -> str:
    """대화 히스토리(role/content 목록)를 받아 최종 답변 텍스트를 반환."""
    client = _client()
    messages = build_messages(history)
    tool_specs = tools.get_tool_specs()

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tool_specs,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "(빈 응답)"

        # assistant 의 tool 호출 메시지를 그대로 추가
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        })

        # 각 tool 실행 결과를 tool 메시지로 추가
        for tc in msg.tool_calls:
            result_json = tools.dispatch_json(tc.function.name, tc.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.function.name,
                "content": result_json,
            })

    # tool 라운드 한도 초과 시 마지막으로 한 번 더 요약 답변 요청
    final = client.chat.completions.create(
        model=MODEL,
        messages=messages + [{
            "role": "user",
            "content": "지금까지 조회한 내용을 바탕으로 최종 답변을 정리해줘.",
        }],
        temperature=0.2,
    )
    return final.choices[0].message.content or "(빈 응답)"
