import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,33))
r=w0.sketch().arc((-89,43),(-98,-10),(-77,-61)).segment((-77,-62)).segment((-76,-62)).arc((-60,-78),(-40,-90)).segment((-36,-93)).segment((-35,-92)).arc((41,-90),(89,-39)).segment((90,-39)).segment((89,-38)).arc((98,12),(77,59)).segment((77,61)).segment((76,62)).arc((60,78),(40,90)).segment((36,93)).segment((35,92)).arc((-41,90),(-89,39)).close().assemble().finalize().extrude(-200).union(w1.sketch().arc((-12,1),(12,4),(-12,2)).arc((-10,2),(-12,1)).assemble().finalize().extrude(-129))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00268618.step')
