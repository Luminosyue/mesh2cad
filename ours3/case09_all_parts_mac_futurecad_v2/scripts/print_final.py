#!/usr/bin/env python3
import json
from pathlib import Path

root = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2')
d = json.loads((root/'metrics/summary.json').read_text())

def b(value):
    return str(bool(value)).lower()

lines = [
    f"CURRENT_GATE={d['CURRENT_GATE']}",
    f"SOURCE_OBJ={d['SOURCE_OBJ']}",
    f"CAD_PART_COUNT={d['CAD_PART_COUNT']}",
    'CAD_PART_LABELS=' + json.dumps(d['CAD_PART_LABELS'], separators=(',',':')),
    f"MAC_API_AVAILABLE={b(d['MAC_API_AVAILABLE'])}",
    f"MAC_PARTS_ATTEMPTED={d['MAC_PARTS_ATTEMPTED']}",
    f"MAC_PARTS_SUCCESS={d['MAC_PARTS_SUCCESS']}",
    f"MAC_PART_RATIO={d['MAC_PART_RATIO']}",
    f"ALL_PARTS_MAC={b(d['ALL_PARTS_MAC'])}",
    f"MAC_RUNS={d['MAC_RUNS']}",
    f"LLM_CALLS={d['LLM_CALLS']}",
    f"TOTAL_INPUT_TOKENS={d['TOTAL_INPUT_TOKENS']}",
    f"TOTAL_OUTPUT_TOKENS={d['TOTAL_OUTPUT_TOKENS']}",
    '--------------------', 'PER PART', '--------------------',
]
for p in d['part_qa']:
    ops = json.dumps(p['FINAL_OP_NAMES'], separators=(',',':'))
    lines.append(f"{p['part_id']} | LABEL={p['label']} | MAC_USED={b(p['MAC_USED'])} | MAC_RUNS={p['MAC_RUNS']} | LLM_CALLS={p['LLM_CALLS']} | FINAL_OPS={ops} | FINAL_Q={p['FINAL_Q']} | FACES={p['FACES']} | FEATURE_Q={p['FEATURE_Q']} | STRUCTURE_Q={p['STRUCTURE_Q']}")
lines += [
    '--------------------', 'FUTURECAD', '--------------------',
    f"FUTURECAD_REPO_FOUND={b(d['FUTURECAD_REPO_FOUND'])}",
    f"FUTURECAD_OFFICIAL_CODE_AVAILABLE={b(d['FUTURECAD_OFFICIAL_CODE_AVAILABLE'])}",
    f"BREPGROUND_CODE_AVAILABLE={b(d['BREPGROUND_CODE_AVAILABLE'])}",
    f"BREPGROUND_WEIGHTS_AVAILABLE={b(d['BREPGROUND_WEIGHTS_AVAILABLE'])}",
    f"FUTURECAD_OFFICIAL_USED={b(d['FUTURECAD_OFFICIAL_USED'])}",
    f"GROUNDING_MODE={d['GROUNDING_MODE']}",
    'GROUNDING_REQUIRED_PARTS=' + json.dumps(d['GROUNDING_REQUIRED_PARTS'], separators=(',',':')),
    f"GROUNDING_QUERIES={d['GROUNDING_QUERIES']}",
    f"GROUNDING_SUCCESS={d['GROUNDING_SUCCESS']}",
    f"GROUNDING_FAILURES={d['GROUNDING_FAILURES']}",
    '--------------------', 'FINAL AIRCRAFT', '--------------------',
    f"FINAL_STEP={d['FINAL_STEP']}",
    f"FINAL_STEP_RELOAD={b(d['FINAL_STEP_RELOAD'])}",
    f"FINAL_BREP_VALID={b(d['FINAL_BREP_VALID'])}",
    f"FINAL_COMPONENT_COUNT={d['FINAL_COMPONENT_COUNT']}",
    f"GEOM_Q={d['GEOM_Q']}",
    f"CHAMFER={d['CHAMFER']}",
    f"P95={d['P95']}",
    f"COVERAGE02={d['COVERAGE02']}",
    f"V1_FACES={d['V1_FACES']}",
    f"V2_FACES={d['V2_FACES']}",
    f"V1_EDGES={d['V1_EDGES']}",
    f"V2_EDGES={d['V2_EDGES']}",
    f"V1_SURFACE_GROUPS={d['V1_SURFACE_GROUPS']}",
    f"V2_SURFACE_GROUPS={d['V2_SURFACE_GROUPS']}",
    f"V1_STRIP_EDGE_COUNT={d['V1_STRIP_EDGE_COUNT']}",
    f"V2_STRIP_EDGE_COUNT={d['V2_STRIP_EDGE_COUNT']}",
    f"V1_SHARP_EDGE_RECALL={d['V1_SHARP_EDGE_RECALL']}",
    f"V2_SHARP_EDGE_RECALL={d['V2_SHARP_EDGE_RECALL']}",
    f"V1_FEATURE_BOUNDARY_RECALL={d['V1_FEATURE_BOUNDARY_RECALL']}",
    f"V2_FEATURE_BOUNDARY_RECALL={d['V2_FEATURE_BOUNDARY_RECALL']}",
    f"V1_MAC_PART_RATIO={d['V1_MAC_PART_RATIO']}",
    f"V2_MAC_PART_RATIO={d['V2_MAC_PART_RATIO']}",
    f"CAD_STRUCTURE_Q={d['CAD_STRUCTURE_Q']}",
    f"ALL_PARTS_MAC_SUCCESS={b(d['ALL_PARTS_MAC_SUCCESS'])}",
    f"COMPARISON_FIGURE={d['COMPARISON_FIGURE']}",
    f"TRUE_EDGE_FIGURE={d['TRUE_EDGE_FIGURE']}",
    f"GROUNDING_FIGURE={d['GROUNDING_FIGURE']}",
    f"REPORT_PATH={d['REPORT_PATH']}",
    f"TESTS_PASSED={d['TESTS_PASSED']}",
    f"TESTS_FAILED={d['TESTS_FAILED']}",
    'BLOCKERS=' + json.dumps(d['BLOCKERS'], separators=(',',':')),
    'STOP',
]
text = '\n'.join(lines) + '\n'
(root/'metrics/final_terminal_output.txt').write_text(text)
print(text, end='')
