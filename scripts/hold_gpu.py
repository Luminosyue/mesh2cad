#!/usr/bin/env python3
"""Detect idle GPUs and occupy a fixed amount of VRAM (default 40 GiB).

Examples:
  # Watch all cards; any nearly-empty one gets 40GB held
  /data/miniconda3/envs/spatiallm/bin/python scripts/hold_gpu.py

  # Only consider GPU 0,2,5; hold at most 2 cards; poll every 3s
  python scripts/hold_gpu.py --gpus 0,2,5 --max-gpus 2 --poll 3

  # Treat as empty when used < 2GB, occupy 40GB
  python scripts/hold_gpu.py --idle-used-gb 2 --occupy-gb 40

Ctrl+C releases all held memory and exits.
"""

from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional, Set, Tuple


def query_gpus() -> List[Tuple[int, int, int]]:
    """Return list of (index, used_mib, free_mib)."""
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,memory.used,memory.free",
        "--format=csv,noheader,nounits",
    ]
    out = subprocess.check_output(cmd, text=True)
    rows: List[Tuple[int, int, int]] = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        rows.append((int(parts[0]), int(float(parts[1])), int(float(parts[2]))))
    return rows


def parse_gpu_list(s: Optional[str]) -> Optional[Set[int]]:
    if not s:
        return None
    return {int(x.strip()) for x in s.split(",") if x.strip() != ""}


def allocate_on_device(gpu_id: int, occupy_gib: float):
    import torch

    torch.cuda.set_device(gpu_id)
    # float32: 4 bytes/elem. Leave a little headroom for CUDA context / fragmentation.
    target_bytes = int(occupy_gib * (1024**3))
    elems = target_bytes // 4
    # Allocate in chunks to survive fragmentation better.
    chunk = 256 * 1024 * 1024 // 4  # 256 MiB chunks
    bufs = []
    remaining = elems
    while remaining > 0:
        n = min(chunk, remaining)
        try:
            t = torch.empty(n, dtype=torch.float32, device=f"cuda:{gpu_id}")
            t.fill_(0.0)  # force physical allocation
            bufs.append(t)
            remaining -= n
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                # Shrink chunk and retry a few times, then stop at what we got.
                if chunk <= 1024 * 1024 // 4:
                    break
                chunk //= 2
                torch.cuda.empty_cache()
                continue
            raise
    used = sum(b.numel() * 4 for b in bufs) / (1024**3)
    print(
        f"[{time.strftime('%F %T')}] HOLD GPU={gpu_id} occupied≈{used:.2f} GiB "
        f"(target={occupy_gib})",
        flush=True,
    )
    return bufs


def main() -> int:
    ap = argparse.ArgumentParser(description="Occupy idle GPUs with fixed VRAM.")
    ap.add_argument("--occupy-gb", type=float, default=40.0, help="VRAM to hold per GPU (GiB)")
    ap.add_argument(
        "--idle-used-gb",
        type=float,
        default=1.0,
        help="GPU is empty if used memory < this (GiB)",
    )
    ap.add_argument(
        "--min-free-gb",
        type=float,
        default=None,
        help="Also require free >= this (default: occupy-gb + 1)",
    )
    ap.add_argument("--gpus", type=str, default=None, help="Candidate GPU ids, e.g. 0,1,3")
    ap.add_argument("--max-gpus", type=int, default=1, help="Max number of GPUs to hold")
    ap.add_argument("--poll", type=float, default=2.0, help="Poll interval seconds")
    ap.add_argument(
        "--once",
        action="store_true",
        help="Exit after first successful hold (still keeps process alive holding memory)",
    )
    args = ap.parse_args()

    candidates = parse_gpu_list(args.gpus)
    idle_used_mib = int(args.idle_used_gb * 1024)
    min_free_mib = int((args.min_free_gb if args.min_free_gb is not None else args.occupy_gb + 1) * 1024)

    held: Dict[int, list] = {}
    stop = False

    def _stop(*_):
        nonlocal stop
        stop = True
        print(f"\n[{time.strftime('%F %T')}] releasing {list(held.keys())} …", flush=True)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    print(
        f"[{time.strftime('%F %T')}] watch start "
        f"occupy={args.occupy_gb}GiB idle_used<{args.idle_used_gb}GiB "
        f"min_free>={min_free_mib / 1024:.1f}GiB max_gpus={args.max_gpus} "
        f"candidates={sorted(candidates) if candidates else 'all'} poll={args.poll}s",
        flush=True,
    )

    last_wait_log = 0.0
    while not stop:
        if len(held) >= args.max_gpus:
            # Just keep holding; light heartbeat every 60s
            if time.time() - last_wait_log > 60:
                print(
                    f"[{time.strftime('%F %T')}] holding GPUs={sorted(held.keys())}",
                    flush=True,
                )
                last_wait_log = time.time()
            time.sleep(args.poll)
            continue

        try:
            rows = query_gpus()
        except Exception as e:
            print(f"[{time.strftime('%F %T')}] nvidia-smi failed: {e}", flush=True)
            time.sleep(max(args.poll, 5.0))
            continue

        picked = None
        for idx, used, free in rows:
            if candidates is not None and idx not in candidates:
                continue
            if idx in held:
                continue
            if used <= idle_used_mib and free >= min_free_mib:
                picked = (idx, used, free)
                break

        if picked is None:
            if time.time() - last_wait_log > 10:
                status = ", ".join(f"G{i}:used={u}MiB/free={f}MiB" for i, u, f in rows)
                print(f"[{time.strftime('%F %T')}] waiting… {status}", flush=True)
                last_wait_log = time.time()
            time.sleep(args.poll)
            continue

        gpu_id, used, free = picked
        print(
            f"[{time.strftime('%F %T')}] empty GPU={gpu_id} used={used}MiB free={free}MiB — allocating",
            flush=True,
        )
        try:
            held[gpu_id] = allocate_on_device(gpu_id, args.occupy_gb)
        except Exception as e:
            print(f"[{time.strftime('%F %T')}] allocate failed on GPU={gpu_id}: {e}", flush=True)
            time.sleep(args.poll)
            continue

        if args.once or len(held) >= args.max_gpus:
            print(
                f"[{time.strftime('%F %T')}] hold complete GPUs={sorted(held.keys())}; "
                "sleeping until Ctrl+C",
                flush=True,
            )

    held.clear()
    try:
        import torch

        torch.cuda.empty_cache()
    except Exception:
        pass
    print(f"[{time.strftime('%F %T')}] exit", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
