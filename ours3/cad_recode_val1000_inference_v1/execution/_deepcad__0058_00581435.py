import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,19))
r=w0.sketch().arc((-88,-48),(41,61),(-16,-99)).arc((51,86),(-88,-48)).assemble().finalize().extrude(-200).union(w0.sketch().segment((-29,96),(29,96)).arc((0,100),(-29,96)).assemble().finalize().extrude(-111)).union(w1.workplane(offset=-92/2).cylinder(92,90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00581435.step')
