from pathlib import Path
import json,zipfile,hashlib,collections,time
from rebuild_cases import ROOT,RUN,dump
from summarize_cases import summarize

def main():
    summary=summarize()
    assert summary['counts'].get('PENDING',0)==0
    manifest=[]
    # Compact portable code bundle: each part script can rebuild its own STEP.
    with zipfile.ZipFile(RUN/'all_cadquery_scripts.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(RUN/'README.md','README.md');z.write(RUN/'summary.json','summary.json')
        for row in summary['case_results']:
            case=ROOT/row['case']
            for f in sorted((case/'xpart_parts_cadquery_features').rglob('*.py')):
                z.write(f,str(f.relative_to(ROOT)))
            assembly=case/'xpart_parts_cadquery_assembly'/'rebuild_assembly.py'
            if assembly.exists():z.write(assembly,str(assembly.relative_to(ROOT)))
    for row in summary['case_results']:
        case=ROOT/row['case'];files=[]
        for sub in ['xpart_parts_cadquery_features','xpart_parts_cadquery_assembly']:
            for f in sorted((case/sub).rglob('*')):
                if not f.is_file() or f.suffix in ['.log','.pyc','.tmp'] or 'checkpoint' in f.parts or '__pycache__' in f.parts:continue
                digest=hashlib.sha256()
                with f.open('rb') as handle:
                    for block in iter(lambda:handle.read(4*1024*1024),b''):digest.update(block)
                files.append(dict(path=str(f.relative_to(case)),bytes=f.stat().st_size,sha256=digest.hexdigest()))
        dump(case/'xpart_parts_cadquery_features'/'deliverables_manifest.json',dict(case=case.name,files=files));manifest.append(dict(case=case.name,files=len(files),bytes=sum(f['bytes'] for f in files)))
    dump(RUN/'deliverables_manifest.json',dict(cases=manifest,total_bytes=sum(r['bytes'] for r in manifest),total_files=sum(r['files'] for r in manifest),created=time.time()))
    print('PACKAGED',len(manifest),sum(r['bytes'] for r in manifest),flush=True)

if __name__=='__main__':main()
