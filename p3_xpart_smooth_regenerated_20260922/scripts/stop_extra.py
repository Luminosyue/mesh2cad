from pathlib import Path
import os,signal,json
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
targets=[];children={}
for d in Path('/proc').iterdir():
    if not d.name.isdigit():continue
    try:
        args=(d/'cmdline').read_bytes().split(b'\0');stat=(d/'stat').read_text();ppid=int(stat[stat.rfind(')')+2:].split()[1]);children.setdefault(ppid,[]).append(int(d.name))
        if b'scripts/extra_refine.py' in args and args[0].endswith(b'python3'):targets.append(int(d.name))
    except (OSError,ValueError):pass
def descendants(p):return [p]+[q for c in children.get(p,[]) for q in descendants(c)]
for pid in targets:
    for p in descendants(pid):
        try:os.kill(p,signal.SIGTERM)
        except ProcessLookupError:pass
keys=set()
for p in (root/'refinements').glob('*/*/follow_done.json'):
    if json.loads(p.read_text()).get('status')=='reserved_by_extra_worker':keys.add((p.parent.parent.name,p.parent.name))
for line in (root/'extra_refinement.log').read_text().splitlines():
    words=line.split()
    if words and words[0]=='REFINED':keys.add((words[1],words[2]))
(root/'extra_refinement_inputs.json').write_text(json.dumps([str(root/'cases'/c/p/'report.json') for c,p in sorted(keys)]))
print('Stopped helper parents',targets,'preserved inputs',len(keys))
