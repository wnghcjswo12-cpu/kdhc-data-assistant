"""API 연결 진단 도구.

사용법:
  py diagnose.py                 # 7개 엔드포인트 상태 점검
  py diagnose.py fuel            # 특정 데이터셋을 현재 설정(DATASET_SPEC)으로 호출
  py diagnose.py fuel 2024 12    # 연/월 지정 호출
  py diagnose.py raw fuel startDate=20240101 endDate=20241231
                                 # 임의 파라미터로 직접 호출(명세 검증용)

명세(참고문서)를 받으면 raw 모드로 정확한 파라미터를 바로 시험해보고,
맞는 조합을 kdhc_api.DATASET_SPEC 에 반영하면 된다.
"""

from __future__ import annotations

import sys

import requests

import kdhc_api


def check_all() -> None:
    if not kdhc_api.KDHC_API_KEY:
        print("⚠️ KDHC_API_KEY 가 .env 에 없습니다.")
        return
    print(f"KDHC_API_KEY 길이: {len(kdhc_api.KDHC_API_KEY)}자\n")
    for ds, spec in kdhc_api.DATASET_SPEC.items():
        try:
            r = requests.get(
                spec["endpoint"],
                params={"serviceKey": kdhc_api.KDHC_API_KEY, **kdhc_api.COMMON_PARAMS},
                timeout=15,
            )
            print(f"[{ds:11}] {r.status_code}  {r.text[:80].strip()}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{ds:11}] ERROR {exc}")


def call_dataset(dataset: str, year: int | None, month: int | None) -> None:
    try:
        r = kdhc_api.fetch(dataset, year=year, month=month)
        print(f"성공: {r['dataset_name']} / count={r['count']}")
        print("요청 파라미터:", r["params"])
        for item in r["items"][:3]:
            print(" -", item)
    except kdhc_api.KdhcApiError as exc:
        print("실패:", exc)


def call_raw(dataset: str, kv_pairs: list[str]) -> None:
    """임의 파라미터로 직접 호출 — 명세 검증용."""
    spec = kdhc_api.DATASET_SPEC.get(dataset)
    if not spec:
        print("알 수 없는 데이터셋:", dataset)
        return
    params = {"serviceKey": kdhc_api.KDHC_API_KEY, **kdhc_api.COMMON_PARAMS}
    for pair in kv_pairs:
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = v
    r = requests.get(spec["endpoint"], params=params, timeout=20)
    safe = {k: v for k, v in params.items() if k != "serviceKey"}
    print("요청:", spec["endpoint"], safe)
    print("상태:", r.status_code)
    print("본문:", r.text[:800])


def main() -> None:
    args = sys.argv[1:]
    if not args:
        check_all()
    elif args[0] == "raw" and len(args) >= 2:
        call_raw(args[1], args[2:])
    else:
        dataset = args[0]
        year = int(args[1]) if len(args) >= 2 else None
        month = int(args[2]) if len(args) >= 3 else None
        call_dataset(dataset, year, month)


if __name__ == "__main__":
    main()
