#!/usr/bin/env python3
import argparse

from routeb_dora_geometry_pipeline import run_full


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parts", nargs="+", required=True)
    p.add_argument("--resume", action="store_true")
    a = p.parse_args()
    a.skip_stage1 = True
    a.skip_stage2 = False
    a.only_stage1 = False
    return run_full(a)


if __name__ == "__main__":
    raise SystemExit(main())
