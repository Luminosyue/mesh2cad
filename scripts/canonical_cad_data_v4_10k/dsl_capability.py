#!/usr/bin/env python3
"""Capability declaration tied to the frozen placement_v3 executor; no approximations."""
from __future__ import annotations
import hashlib, json
from .config import DATA_ROOT, EXECUTOR, EXECUTOR_SHA256

ROWS = [
 ('Line','PARTIAL','Sketch primitive not standalone executable','PARTIAL'), ('Circle','SUPPORTED','Extrude(Circle)','COMPLETE'),
 ('Arc','UNSUPPORTED','No ARC primitive','NONE'), ('Ellipse','UNSUPPORTED','No ellipse primitive','NONE'), ('BSpline','UNSUPPORTED','No BSpline primitive','NONE'),
 ('Extrude','SUPPORTED','Circle and polygon extrusions','PARTIAL'), ('Cut','SUPPORTED','Binary Cut','COMPLETE'), ('Join','SUPPORTED','Union','COMPLETE'),
 ('Revolve','PARTIAL','Cylinder-equivalent only; no general profile revolve','PARTIAL'), ('Loft','UNSUPPORTED','No lossless Loft','NONE'),
 ('Sweep','UNSUPPORTED','No lossless Sweep','NONE'), ('Fillet','UNSUPPORTED','No Fillet','NONE'), ('Chamfer','UNSUPPORTED','No Chamfer','NONE'),
 ('Shell','UNSUPPORTED','No Shell','NONE'), ('Mirror','UNSUPPORTED','No Mirror','NONE'), ('Pattern','UNSUPPORTED','No Pattern','NONE'),
]
def main():
 out = DATA_ROOT / 'reports/02_DSL_CAPABILITY_MATRIX.json'
 if out.exists(): raise FileExistsError(f'refusing to overwrite: {out}')
 actual = hashlib.sha256(EXECUTOR.read_bytes()).hexdigest()
 report = {'executor_module':str(EXECUTOR),'executor_sha256_expected':EXECUTOR_SHA256,'executor_sha256_actual':actual,'no_lossy_approximations_allowed':True,
           'matrix':[{'operation':a,'support':b,'notes':c,'parameter_complete':d} for a,b,c,d in ROWS]}
 out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report,indent=2)+'\n'); print(out)
if __name__ == '__main__': main()
