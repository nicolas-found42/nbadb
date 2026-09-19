from __future__ import annotations

import os
import subprocess
import time

import requests

STATS_HEADERS = {
    "Host": "stats.nba.com",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nba.com/",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

_CURL_HEADERS = tuple(STATS_HEADERS.items()) + (
    (
        "Sec-Ch-Ua",
        '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    ),
    ("Sec-Ch-Ua-Mobile", "?0"),
    ("Sec-Fetch-Dest", "empty"),
)

_TARGET_URL = "https://stats.nba.com/stats/commonallplayers"
_TARGET_PARAMS = {"LeagueID": "00", "Season": "2024-25", "IsOnlyCurrentSeason": "1"}


def _print_env() -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"):
        print(f"env {key}={os.environ.get(key)!r}", flush=True)


def _requests_attempt(index: int, *, fresh_session: bool) -> None:
    started = time.monotonic()
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            _TARGET_URL,
            params=_TARGET_PARAMS,  # type: ignore[arg-type]
            headers=STATS_HEADERS,
            timeout=(10.0, 20.0),
            proxies={},
        )
        elapsed = time.monotonic() - started
        print(
            f"round {index} requests({'fresh' if fresh_session else 'shared'}) "
            f"OK after {elapsed:.1f}s status={response.status_code} bytes={len(response.content)}",
            flush=True,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - started
        print(
            f"round {index} requests({'fresh' if fresh_session else 'shared'}) "
            f"FAIL after {elapsed:.1f}s: {type(exc).__name__}: {exc}",
            flush=True,
        )
    finally:
        session.close()


def _curl_attempt(index: int) -> None:
    cmd = [
        "curl",
        "-sS",
        "--compressed",
        "--connect-timeout",
        "5",
        "--max-time",
        "20",
        "-o",
        "/tmp/curl_probe_out.json",
        "-w",
        "%{http_code} %{time_total} %{size_download}",
    ]
    for name, value in _CURL_HEADERS:
        cmd.extend(("-H", f"{name}: {value}"))
    cmd.append(f"{_TARGET_URL}?LeagueID=00&Season=2024-25&IsOnlyCurrentSeason=1")
    started = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    elapsed = time.monotonic() - started
    print(
        f"round {index} curl rc={result.returncode} elapsed={elapsed:.1f}s "
        f"stdout={result.stdout!r} stderr={result.stderr.strip()!r}",
        flush=True,
    )


def main() -> int:
    _print_env()
    for i in range(1, 7):
        _requests_attempt(i, fresh_session=True)
        _curl_attempt(i)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
