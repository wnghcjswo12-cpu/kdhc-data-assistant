"""한국지역난방공사 공공데이터 API 호출 계층.

7개 공공데이터포털 서비스를 호출한다. 인증키는 .env 의 KDHC_API_KEY 에서만
읽으며, 코드에 하드코딩하지 않는다.

────────────────────────────────────────────────────────────────────────
⚠️ 명세 확인 후 조정할 곳: 아래 DATASET_SPEC 한 곳만 고치면 된다.
   각 서비스의 "참고문서(요청변수 표)"를 보고 period 파라미터명과
   날짜 형식만 맞추면 전체가 동작한다.
   (현재는 data.go.kr 표준 추정값. 실제 호출은 'Unexpected errors(500)'
    응답을 받았으며, 정확한 요청변수가 확인되면 즉시 동작한다.)
────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

KDHC_API_KEY = os.getenv("KDHC_API_KEY", "").strip()

# ── 데이터셋 정의 ─────────────────────────────────────────────────────
# period.mode 설명:
#   "range_ymd" : 시작일/종료일을 YYYYMMDD 로 보냄  (start/end 파라미터명 사용)
#   "range_ym"  : 시작월/종료월을 YYYYMM 로 보냄
#   "single_ym" : 단일 기준월(param) 을 YYYYMM 으로 보냄
#   "year_month": 연도/월을 각각 정수 파라미터(year_param/month_param)로 보냄
# 명세를 받으면 각 서비스의 mode/param 이름/fmt 만 교체하면 된다.
DATASET_SPEC: dict[str, dict[str, Any]] = {
    "fuel": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcFuel",
        "name": "연료사용량",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "power_prod": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcPwrProd",
        "name": "발전소 생산실적",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "power_sell": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcPowerSell",
        "name": "전기판매량(GW)",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "heat_sell": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcHeatSell",
        "name": "열판매량",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "heat_prod": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcHeatProd",
        "name": "열생산량(GW)",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "energy": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcEnergy",
        "name": "에너지사용량",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
    "weather": {
        "endpoint": "https://apis.data.go.kr/B550373/kdhcWeatherObser",
        "name": "기상관측정보",
        "period": {"mode": "range_ymd", "start": "startDate", "end": "endDate", "fmt": "%Y%m%d"},
    },
}

# 하위호환 별칭
ENDPOINTS: dict[str, str] = {k: v["endpoint"] for k, v in DATASET_SPEC.items()}
DATASET_NAMES: dict[str, str] = {k: v["name"] for k, v in DATASET_SPEC.items()}

# 공통 요청 파라미터 (명세 확인 후 type/returnType 등 조정 가능)
COMMON_PARAMS: dict[str, Any] = {
    "pageNo": 1,
    "numOfRows": 500,
    "type": "json",
}

_TIMEOUT = 20


class KdhcApiError(Exception):
    """API 호출/파싱 중 발생한 오류."""


def _require_key() -> None:
    if not KDHC_API_KEY:
        raise KdhcApiError(
            "KDHC_API_KEY 가 설정되지 않았습니다. .env 파일에 인증키를 입력하세요."
        )


def recent_12_months() -> list[tuple[int, int]]:
    """오늘 기준 최근 12개월의 (year, month) 목록을 오래된 순으로 반환."""
    today = date.today()
    months: list[tuple[int, int]] = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(months))


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """해당 월의 1일과 말일을 반환."""
    first = date(year, month, 1)
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    last = date(nxt.toordinal() - 1)
    return first, last


def _period_params(spec_period: dict[str, Any],
                   year: int | None, month: int | None) -> dict[str, str]:
    """DATASET_SPEC.period 설정과 year/month 로 실제 기간 파라미터를 만든다.

    - year/month 둘 다 없으면 최근 12개월 범위.
    - year 만 있으면 그 해 전체.
    - year+month 면 그 달.
    """
    mode = spec_period["mode"]
    today = date.today()

    # 조회 구간(시작/끝 날짜) 결정
    if year is None and month is None:
        months = recent_12_months()
        start_y, start_m = months[0]
        start_d = date(start_y, start_m, 1)
        end_d = today
    elif year is not None and month is None:
        start_d = date(year, 1, 1)
        end_d = date(year, 12, 31)
    else:
        y = year if year is not None else today.year
        m = month if month is not None else today.month
        start_d, end_d = _month_bounds(y, m)

    if mode == "range_ymd":
        fmt = spec_period.get("fmt", "%Y%m%d")
        return {
            spec_period["start"]: start_d.strftime(fmt),
            spec_period["end"]: end_d.strftime(fmt),
        }
    if mode == "range_ym":
        return {
            spec_period["start"]: start_d.strftime("%Y%m"),
            spec_period["end"]: end_d.strftime("%Y%m"),
        }
    if mode == "single_ym":
        return {spec_period["param"]: end_d.strftime("%Y%m")}
    if mode == "year_month":
        out = {spec_period["year_param"]: str(end_d.year)}
        if month is not None:
            out[spec_period["month_param"]] = str(end_d.month)
        return out
    return {}


def _extract_items(payload: Any) -> list[dict]:
    """data.go.kr 표준 JSON 응답에서 item 목록을 방어적으로 꺼낸다."""
    if payload is None:
        return []
    node: Any = payload
    if isinstance(node, dict) and "response" in node:
        node = node.get("response", {})
    body = node.get("body", node) if isinstance(node, dict) else {}
    items = body.get("items", body) if isinstance(body, dict) else body
    if isinstance(items, dict) and "item" in items:
        items = items["item"]
    if isinstance(items, dict):
        items = [items]
    if items is None:
        return []
    if isinstance(items, list):
        return [it for it in items if isinstance(it, dict)]
    return []


def _request(dataset: str, params: dict[str, Any]) -> dict[str, Any]:
    """단일 서비스 호출 후 표준화된 결과 딕셔너리를 반환."""
    _require_key()
    if dataset not in DATASET_SPEC:
        raise KdhcApiError(f"알 수 없는 데이터셋: {dataset}")

    spec = DATASET_SPEC[dataset]
    query = {
        "serviceKey": KDHC_API_KEY,
        **COMMON_PARAMS,
        **{k: v for k, v in params.items() if v is not None},
    }

    try:
        resp = requests.get(spec["endpoint"], params=query, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        # 서버가 본문에 단서를 담을 수 있어 함께 노출
        detail = ""
        if getattr(exc, "response", None) is not None:
            detail = f" | 응답: {exc.response.text[:200]}"
        raise KdhcApiError(f"{spec['name']} 호출 실패: {exc}{detail}") from exc

    try:
        payload = resp.json()
    except ValueError:
        raise KdhcApiError(
            f"{spec['name']} 응답을 JSON 으로 해석하지 못했습니다. "
            f"응답 일부: {resp.text[:300]}"
        )

    items = _extract_items(payload)
    return {
        "dataset": dataset,
        "dataset_name": spec["name"],
        "params": {k: v for k, v in query.items() if k != "serviceKey"},
        "count": len(items),
        "items": items,
    }


def fetch(dataset: str, year: int | None = None, month: int | None = None,
          **extra: Any) -> dict[str, Any]:
    """지정 데이터셋을 조회한다. 기간 미지정 시 최근 12개월."""
    if dataset not in DATASET_SPEC:
        raise KdhcApiError(f"알 수 없는 데이터셋: {dataset}")
    period = _period_params(DATASET_SPEC[dataset]["period"], year, month)
    return _request(dataset, {**period, **extra})
