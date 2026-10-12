from regenerate_smooth import *
from datetime import datetime,timezone
files=sorted(p for p in ROOT.glob('*/xpart_parts/PART_*/complete_part_*.obj') if p.relative_to(ROOT).parts[0]!='tank')
s=summary(files);assert len(files)==793 and s['cases']==77 and s['complete_artifact_count']==793
for src in files:
    od=OUT/'cases'/src.relative_to(ROOT).parts[0]/src.parent.name
    audit=json.loads((OUT/'validation'/od.parent.name/(od.name+'.json')).read_text())
    assert audit['passed'],str(od)
    for name,expected in audit['hashes'].items():assert hashlib.sha256((od/name).read_bytes()).hexdigest()==expected,(str(od),name)
assert not (OUT/'cases/tank').exists()
receipt=dict(completed_utc=datetime.now(timezone.utc).isoformat(),status='completed_with_quality_exceptions',parts=793,cases=77,complete_artifacts=793,independently_rebuilt_and_verified=793,quality_status=s['status_counts'],tank_skipped=True,original_inputs_unchanged=True)
dump(OUT/'delivery_receipt.json',receipt);dump(OUT/'pipeline_done.json',receipt)
subprocess.run([sys.executable,str(SCRIPTS/'make_review.py')],check=True)
shutil.copy2(OUT/'delivery_receipt.json',OUT/'review/delivery_receipt.json')
print(json.dumps(receipt),flush=True)
