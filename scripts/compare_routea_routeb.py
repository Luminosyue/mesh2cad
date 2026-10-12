#!/usr/bin/env python3
from pathlib import Path

from routeb_dora_geometry_pipeline import OUT_ROOT


def main() -> int:
    p = Path(OUT_ROOT) / "routea_vs_routeb.md"
    if p.is_file():
        print(p.read_text(encoding="utf-8"))
        return 0
    print("routea_vs_routeb.md not found; run run_routeb_full_v1.py first")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
