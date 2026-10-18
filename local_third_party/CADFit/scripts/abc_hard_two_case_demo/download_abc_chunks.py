#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from common import ensure_demo_dirs, sha256_file


OFFICIAL_HANDLE = "https://archive.nyu.edu/handle/2451/44309"


def parse_chunks(chunks: str) -> list[str]:
    out = []
    for part in chunks.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(f"{int(part):04d}" if part.isdigit() else part)
    return out


def official_links() -> dict[tuple[str, str], str]:
    # NYU's handle page mixes unrelated hrefs and file names in separate
    # table cells, so regex pairing can produce false links. Use the verified
    # bitstream fallback below instead of trusting a loose HTML parse.
    return {}
    html = urllib.request.urlopen(OFFICIAL_HANDLE, timeout=30).read().decode("utf-8", "ignore")
    links: dict[tuple[str, str], str] = {}
    for href, name, chunk, kind in re.findall(r'href="([^"]+)".*?(abc_(\d{4})_(step|stl2)_v00\.7z)', html, flags=re.I | re.S):
        url = href if href.startswith("http") else "https://archive.nyu.edu" + href
        links[(chunk, kind)] = url
    return links


def verified_url(chunk: str, kind: str, discovered: dict[tuple[str, str], str]) -> str:
    if (chunk, kind) in discovered:
        return discovered[(chunk, kind)]
    # The fallback is still verified with wget --spider before use.
    bitstream = 3 + int(chunk) * 3 + (0 if kind == "step" else 1)
    return f"https://archive.nyu.edu/bitstream/2451/44309/{bitstream}/abc_{chunk}_{kind}_v00.7z"


def run(cmd: list[str], log_path: Path | None = None) -> int:
    if log_path:
        with log_path.open("ab") as f:
            return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    return subprocess.run(cmd).returncode


def download(url: str, dst: Path, skip_existing: bool) -> str:
    spider = subprocess.run(["wget", "--spider", "-S", "-T", "30", url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if spider.returncode != 0:
        raise RuntimeError(f"Official URL not reachable: {url}\n{spider.stdout[-1000:]}")
    m = re.search(r"Content-Length:\s*(\d+)", spider.stdout, flags=re.I)
    expected_size = int(m.group(1)) if m else None
    if skip_existing and dst.exists() and dst.stat().st_size > 0:
        if expected_size is None or dst.stat().st_size == expected_size:
            return "skipped"
    tmp = dst.with_suffix(dst.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    rc = run(["wget", "-c", "-O", str(tmp), url])
    if rc != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        raise RuntimeError(f"Download failed for {url}")
    os.replace(tmp, dst)
    return "downloaded"


def extract_archive(archive: Path, out_dir: Path, log_dir: Path) -> None:
    marker = out_dir / ".extracted"
    if marker.exists():
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / (archive.name + ".extract.log")
    rc = run(["7z", "x", "-y", f"-o{out_dir}", str(archive)], log)
    if rc != 0:
        raise RuntimeError(f"7z extraction failed for {archive}; see {log}")
    marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", required=True, help="Comma-separated chunk ids, e.g. 0000,0001")
    ap.add_argument("--data-root", default="data/abc_v00_demo")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--max-chunks", type=int, default=3)
    args = ap.parse_args()
    ensure_demo_dirs()
    chunks = parse_chunks(args.chunks)[: args.max_chunks]
    data = Path(args.data_root)
    archives = data / "archives"
    manifest_path = Path("artifacts/abc_hard_two_case_demo/download_manifest.csv")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    discovered = official_links()
    rows = []
    if manifest_path.exists():
        with manifest_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    for chunk in chunks:
        for kind in ["step", "stl2"]:
            url = verified_url(chunk, kind, discovered)
            dst = archives / f"abc_{chunk}_{kind}_v00.7z"
            try:
                status = download(url, dst, args.skip_existing)
                digest = sha256_file(dst)
                if args.extract:
                    extract_archive(dst, data / kind / chunk, archives)
                rows.append({
                    "chunk_id": chunk, "kind": kind, "url": url, "archive_path": str(dst),
                    "status": status, "sha256": digest, "bytes": dst.stat().st_size,
                    "extracted": bool(args.extract),
                })
                print(f"DOWNLOAD {chunk} {kind} {status} {dst.stat().st_size}")
            except Exception as e:
                rows.append({"chunk_id": chunk, "kind": kind, "url": url, "archive_path": str(dst), "status": "failed", "sha256": "", "bytes": "", "extracted": False, "error": repr(e)})
                print(f"DOWNLOAD_FAIL {chunk} {kind} {e}", file=sys.stderr)
                return 2
        # Immediate index/scan hook after each complete chunk.
        subprocess.run([sys.executable, "scripts/abc_hard_two_case_demo/index_abc_files.py"], check=False)
        subprocess.run([sys.executable, "scripts/abc_hard_two_case_demo/scan_step_faces.py", "--resume"], check=False)
    fields = ["chunk_id", "kind", "url", "archive_path", "status", "sha256", "bytes", "extracted", "error"]
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
