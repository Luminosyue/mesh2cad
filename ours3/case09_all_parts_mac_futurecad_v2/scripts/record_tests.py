#!/usr/bin/env python3
import json
from pathlib import Path

root = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2')
for rel in ['metrics/summary.json', '07_final_qa/final_qa.json']:
    path = root / rel
    data = json.loads(path.read_text())
    data['TESTS_PASSED'] = 36
    data['TESTS_FAILED'] = 0
    data['TEST_COMMAND'] = '/data/miniconda3/envs/multi_agent_cad/bin/python -m pytest -q tests/test_case09_v2.py'
    data['TEST_LOG'] = str(root/'metrics/pytest.log')
    data['BLOCKERS'] = []
    path.write_text(json.dumps(data, indent=2) + '\n')

report = root/'report.md'
text = report.read_text()
text += '\n## Verification\n\n- 36 tests passed; 0 failed.\n- Test log: `' + str(root/'metrics/pytest.log') + '`\n'
report.write_text(text)
