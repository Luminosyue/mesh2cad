import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-52))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-15,-14),(17,-11),(12,17)).arc((10,16),(8,16)).arc((-1,-10),(-15,-14)).assemble().finalize().extrude(81).union(w0.sketch().arc((-2,-6),(18,-10),(10,10)).arc((11,14),(11,17)).segment((15,14)).segment((14,13)).arc((15,10),(13,8)).segment((12,7)).segment((11,8)).arc((10,9),(10,10)).segment((10,11)).close().assemble().finalize().extrude(136)).union(w0.sketch().arc((14,14),(16,10),(17,6)).segment((21,2)).arc((19,8),(14,14)).assemble().finalize().extrude(152)).union(w1.workplane(offset=73/2).moveTo(-1,-1).cylinder(73,19))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00249276.step')
