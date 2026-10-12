"""Package the completed factory without overwriting an existing delivery."""
import json,tarfile,hashlib
from factory import ROOT
status=json.loads((ROOT/'reports/final/status.json').read_text())
checks=json.loads((ROOT/'reports/delivery_checks_v2.json').read_text())
if not checks['pass']:raise RuntimeError('Delivery replay/raw source validation failed')
if status['overall']['completed']!=100:raise RuntimeError('Frozen run is incomplete')
archive=ROOT.parent/(ROOT.name+'_delivery.tar.gz')
with tarfile.open(archive,'x:gz') as tar:tar.add(ROOT,arcname=ROOT.name)
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
with archive.with_suffix(archive.suffix+'.sha256').open('x') as f:f.write(digest+'  '+archive.name+'\n')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest}))
