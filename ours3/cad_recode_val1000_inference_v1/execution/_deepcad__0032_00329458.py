import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-86,0))
r=w0.workplane(offset=162/2).cylinder(162,20).union(w0.workplane(offset=200/2).moveTo(-3,0).cylinder(200,16)).union(w1.sketch().segment((-9,-18),(-9,18)).arc((-20,0),(-9,-18)).assemble().finalize().extrude(148))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00329458.step')
