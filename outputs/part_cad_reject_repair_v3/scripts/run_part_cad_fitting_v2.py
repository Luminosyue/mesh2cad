"""Resume the frozen experiment; never delete or replace completed case results."""
import os
import subprocess
import sys
from pathlib import Path

O = Path(__file__).resolve().parents[1]
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

def run(name, *args):
    subprocess.run([sys.executable, '-B', str(O / 'scripts' / name), *args], check=True)

if not (O / 'manifests/cases.json').exists():
    run('v2_prepare.py')
for stage in ['near', 'reject', 'strict']:
    if stage == 'reject' and not (O / 'reports/NEAR_GATE.json').exists():
        raise SystemExit('Review the complete Near results and record NEAR_GATE.json before Reject fitting.')
    run('v2_features.py', '--group', stage)
    run('v2_plan.py', '--group', stage)
    run('v2_run.py', '--group', stage)
    if stage == 'near':
        run('v2_report.py', '--near-only')
run('v2_report.py')
run('v2_validate.py')
run('v2_visualize.py')
run('v2_final_readout.py')
