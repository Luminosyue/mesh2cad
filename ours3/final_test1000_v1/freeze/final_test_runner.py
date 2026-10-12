#!/usr/bin/env python3
import os, runpy, sys
from pathlib import Path
ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
FINAL = ROOT/'ours3/final_test1000_v1'
ARM = os.environ.get('FINAL_ARM', '').lower()
if ARM in ('a1', 'a2'):
    os.environ['CAD_SECOND_STREAM'] = 'curve_tokens'
    os.environ['CAD_USE_SEPARATE_EDGE_TOKENS'] = '1'
    os.environ['REQUIRE_CURVE_TOKEN_REGISTRY'] = '1'
    os.environ['CURVE_TOKEN_ROOT'] = str(ROOT/'ours3/exact9998_curve_tokens_c2_v1')
    os.environ['CURVE_TOKEN_REGISTRY'] = str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl')
    os.environ['CURVE_ABLATION_ARM'] = ARM
    os.environ['CURVE_ABLATION_VIEW'] = str(ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1'/('A1_LINE_CURVE_VIEW.jsonl' if ARM == 'a1' else 'A2_NONLINE_CURVE_VIEW.jsonl'))
    import curve_ablation_runtime
    curve_ablation_runtime.install()
else:
    os.environ.pop('CURVE_ABLATION_ARM', None)
    os.environ.pop('CURVE_ABLATION_VIEW', None)
entry = ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/launch/unified_v2_entrypoint.py'
runpy.run_path(str(entry), run_name='__main__')
