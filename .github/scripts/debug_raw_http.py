from __future__ import annotations

import os
import socket
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


def _print_env() -> None:
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "NBADB_REQUEST_TIMEOUT",
        "NBADB_REQUEST_TIMEOUT_CAP",
        "REQUESTS_CA_BUNDLE",
        "SSL_CERT_FILE",
    ):
        print(f"env {key}={os.environ.get(key)!r}", flush=True)
    print(f"socket.getdefaulttimeout()={socket.getdefaulttimeout()}", flush=True)


def _raw_socket_connect(host: str, port: int, deadline: float) -> None:
    started = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=deadline) as sock:
            elapsed = time.monotonic() - started
            print(
                f"raw_socket_connect OK after {elapsed:.1f}s local={sock.getsockname()}", flush=True
            )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - started
        print(
            f"raw_socket_connect EXCEPTION after {elapsed:.1f}s: {type(exc).__name__}: {exc}",
            flush=True,
        )


def _dns_resolve(host: str) -> None:
    started = time.monotonic()
    try:
        infos = socket.getaddrinfo(host, 443)
        elapsed = time.monotonic() - started
        addrs = sorted({info[4][0] for info in infos})
        print(f"dns_resolve OK after {elapsed:.2f}s addrs={addrs}", flush=True)
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - started
        print(
            f"dns_resolve EXCEPTION after {elapsed:.2f}s: {type(exc).__name__}: {exc}", flush=True
        )


def _raw_requests_get(url: str, params: dict[str, object], timeout: tuple[float, float]) -> None:
    started = time.monotonic()
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            url,
            params=params,
            headers=STATS_HEADERS,
            timeout=timeout,
            proxies={},
        )
        elapsed = time.monotonic() - started
        print(
            f"raw_requests_get OK after {elapsed:.1f}s status={response.status_code} "
            f"bytes={len(response.content)}",
            flush=True,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - started
        cause = exc.__cause__
        print(
            f"raw_requests_get EXCEPTION after {elapsed:.1f}s: {type(exc).__name__}: {exc} "
            f"cause={type(cause).__name__ if cause else None}: {cause}",
            flush=True,
        )


_CURL_HEADERS = (
    ("Host", "stats.nba.com"),
    (
        "User-Agent",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    ),
    ("Accept", "application/json, text/plain, */*"),
    ("Accept-Language", "en-US,en;q=0.5"),
    ("Accept-Encoding", "gzip, deflate, br"),
    ("Connection", "keep-alive"),
    ("Referer", "https://www.nba.com/"),
    ("Pragma", "no-cache"),
    ("Cache-Control", "no-cache"),
    (
        "Sec-Ch-Ua",
        '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    ),
    ("Sec-Ch-Ua-Mobile", "?0"),
    ("Sec-Fetch-Dest", "empty"),
)


def _curl_probe(label: str, url: str, *, max_time: float = 90.0) -> None:
    cmd = [
        "curl",
        "-sS",
        "--compressed",
        "--connect-timeout",
        "5",
        "--max-time",
        str(max_time),
        "-o",
        "/tmp/curl_probe_out.json",
        "-w",
        "%{http_code} %{time_total} %{size_download}",
    ]
    for name, value in _CURL_HEADERS:
        cmd.extend(("-H", f"{name}: {value}"))
    cmd.append(url)
    started = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 15)
    elapsed = time.monotonic() - started
    print(
        f"curl_probe[{label}] rc={result.returncode} elapsed={elapsed:.1f}s "
        f"stdout={result.stdout!r} stderr={result.stderr.strip()!r}",
        flush=True,
    )


def main() -> int:
    _print_env()
    _dns_resolve("stats.nba.com")
    _raw_socket_connect("stats.nba.com", 443, 120.0)
    _raw_requests_get(
        "https://stats.nba.com/stats/commonallplayers",
        {"LeagueID": "00", "Season": "2024-25", "IsOnlyCurrentSeason": "1"},
        timeout=(30.0, 120.0),
    )
    _curl_probe(
        "commonteamyears-control",
        "https://stats.nba.com/stats/commonteamyears?LeagueID=00",
    )
    _curl_probe(
        "commonallplayers-target",
        "https://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=2024-25&IsOnlyCurrentSeason=1",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
