from pathlib import Path
import tempfile,subprocess,time,sys
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
src=r/'cases/building_5i/PART_048/cad.py'
with tempfile.TemporaryDirectory(prefix='stl_tolerance_',dir=r/'validation') as td:
    p=Path(td)/'cad.py';code=src.read_text();assert 'tolerance=0.025/PARAMETERS["construction_scale"]' in code
    p.write_text(code.replace('tolerance=0.025/PARAMETERS["construction_scale"]','tolerance=0.025'))
    t=time.monotonic();result=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,timeout=120)
    print('seconds',time.monotonic()-t,'returncode',result.returncode,'error',result.stderr[-1000:])
    print('outputs',[(x.name,x.stat().st_size) for x in Path(td).iterdir()])
