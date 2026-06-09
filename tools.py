"""GPT 에 노출할 tool(function) 스키마와 디스패처.

데이터셋별로 tool 을 분리해 GPT 가 정확히 선택하도록 한다.
기간(year/month) 미지정 시 kdhc_api.fetch 가 최근 12개월을 조회한다.
"""

from __future__ import annotations

import json
from typing import Any

import kdhc_api

# tool 이름 -> 데이터셋 키
_TOOL_TO_DATASET: dict[str, str] = {
    "get_fuel_usage": "fuel",
    "get_power_production": "power_prod",
    "get_power_sell": "power_sell",
    "get_heat_sell": "heat_sell",
    "get_heat_production": "heat_prod",
    "get_energy_usage": "energy",
    "get_weather_observation": "weather",
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "get_fuel_usage": "한국지역난방공사 연료사용량을 조회한다. 발전·열생산에 사용된 연료량 데이터.",
    "get_power_production": "발전소 생산실적(발전량)을 조회한다.",
    "get_power_sell": "전기판매량(GW)을 조회한다.",
    "get_heat_sell": "지역난방 열판매량을 조회한다.",
    "get_heat_production": "열생산량(GW)을 조회한다.",
    "get_energy_usage": "에너지사용량을 조회한다.",
    "get_weather_observation": "기상관측정보(기온 등)를 조회한다. 수요·생산과 날씨를 비교할 때 사용.",
}


def _params_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "year": {
                "type": "integer",
                "description": "조회 연도(예: 2025). 생략 시 최근 12개월을 조회.",
            },
            "month": {
                "type": "integer",
                "description": "조회 월(1~12). 생략 가능.",
                "minimum": 1,
                "maximum": 12,
            },
        },
        "additionalProperties": False,
    }


def get_tool_specs() -> list[dict[str, Any]]:
    """OpenAI Chat Completions tools 규격 목록을 반환."""
    specs = []
    for name, desc in _TOOL_DESCRIPTIONS.items():
        specs.append({
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": _params_schema(),
            },
        })
    return specs


def dispatch(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """tool 호출을 실제 API 조회로 연결한다."""
    dataset = _TOOL_TO_DATASET.get(tool_name)
    if dataset is None:
        return {"error": f"알 수 없는 tool: {tool_name}"}

    year = arguments.get("year")
    month = arguments.get("month")
    try:
        result = kdhc_api.fetch(dataset, year=year, month=month)
    except kdhc_api.KdhcApiError as exc:
        return {"error": str(exc), "dataset": dataset}

    # 토큰 절약: 너무 많은 레코드는 앞부분만 GPT 에 전달
    items = result.get("items", [])
    truncated = len(items) > 120
    result_for_llm = {
        "dataset_name": result.get("dataset_name"),
        "params": result.get("params"),
        "count": result.get("count"),
        "items": items[:120],
        "truncated": truncated,
    }
    if result.get("errors"):
        result_for_llm["errors"] = result["errors"]
    return result_for_llm


def dispatch_json(tool_name: str, arguments_json: str) -> str:
    """tool_call 의 JSON 인자 문자열을 받아 결과를 JSON 문자열로 반환."""
    try:
        arguments = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError:
        arguments = {}
    result = dispatch(tool_name, arguments)
    return json.dumps(result, ensure_ascii=False)
