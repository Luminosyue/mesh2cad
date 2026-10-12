import json
from pathlib import Path
from OCP.BRep import BRep_Tool
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')

def faces(path):
 r=STEPControl_Reader(); assert r.ReadFile(str(path))==IFSelect_RetDone; r.TransferRoots(); s=r.OneShape(); out=[]; e=TopExp_Explorer(s,TopAbs_FACE)
 while e.More(): out.append(TopoDS.Face_s(e.Current())); e.Next()
 return out

for name,path in [
 ('V7B',ROOT/'v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_005/PRIMARY/candidate.step'),
 ('V7D',ROOT/'v7d_common_boundary_control_net/06_candidates/CADPART_005/v7d_constrained_faces.step'),
]:
 print(name)
 for i,f in enumerate(faces(path)):
  s=BRep_Tool.Surface_s(f)
  print(i,type(s),s.UDegree(),s.VDegree(),s.NbUPoles(),s.NbVPoles(),s.Bounds())
  print('UK',[(s.UKnot(j),s.UMultiplicity(j)) for j in range(1,s.NbUKnots()+1)])
  print('VK',[(s.VKnot(j),s.VMultiplicity(j)) for j in range(1,s.NbVKnots()+1)])

d=json.load(open(ROOT/'v7d_common_boundary_control_net/05_common_control_net/CADPART_005/common_control_net.json'))
print('MASTER',len(d['shared_poles'][0]),d['shared_poles'][0])
