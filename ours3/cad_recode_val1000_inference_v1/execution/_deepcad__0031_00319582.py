import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,44,0))
r=w0.sketch().segment((-100,-21),(-91,-21)).arc((-72,-38),(-50,-50)).segment((-50,-78)).segment((77,-78)).segment((77,-50)).arc((99,-14),(91,28)).segment((91,78)).segment((-100,78)).close().assemble().reset().face(w0.sketch().arc((-40,28),(12,-33),(75,21)).arc((16,12),(-40,28)).assemble(),mode='s').finalize().extrude(-89).union(w0.sketch().segment((-100,-100),(100,-100)).segment((100,87)).segment((75,100)).segment((-100,100)).close().assemble().push([(0,-1)]).circle(60,mode='s').finalize().extrude(-44))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00319582.step')
