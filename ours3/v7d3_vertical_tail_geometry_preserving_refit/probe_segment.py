import json, sys
from pathlib import Path

from OCP.BRep import BRep_Tool
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v7d3_vertical_tail_geometry_preserving_refit'
sys.path.insert(0,str(OUT))
from geometry_preserving_refit.master_compatibility import curve_from_three_poles, make_compatible

r=STEPControl_Reader(); r.ReadFile(str(ROOT/'v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_005/PRIMARY/candidate.step')); r.TransferRoots()
e=TopExp_Explorer(r.OneShape(),TopAbs_FACE); surfaces=[]
while e.More():
    surfaces.append(BRep_Tool.Surface_s(TopoDS.Face_s(e.Current()))); e.Next()
master=json.load(open(ROOT/'v7d_common_boundary_control_net/05_common_control_net/CADPART_005/common_control_net.json'))['shared_poles'][0]
segments=[]
for surface in surfaces[:2]:
    s=surface.Copy(); vals=[s.UKnot(i) for i in range(1,s.NbUKnots()+1)]; cut=vals[-2]
    s.Segment(cut,s.Bounds()[1],s.Bounds()[2],s.Bounds()[3])
    segments.append(s)
    print('segment',s.UDegree(),s.VDegree(),s.NbUPoles(),s.NbVPoles(),s.Bounds(),[s.UKnot(i) for i in range(1,s.NbUKnots()+1)])
c=curve_from_three_poles(master)
a,b,c,p=make_compatible(segments[0],segments[1],c)
print('compatible',a.NbUPoles(),b.NbUPoles(),c.NbPoles(),a.NbVPoles(),b.NbVPoles(),len(p))
