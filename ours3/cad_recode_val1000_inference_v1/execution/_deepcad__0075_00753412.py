import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().arc((-16,0),(-14,-7),(-9,-13)).arc((-5,-15),(-1,-16)).arc((15,5),(-12,10)).arc((-14,5),(-16,0)).assemble().finalize().extrude(-200).union(w0.workplane(offset=-64/2).cylinder(64,16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00753412.step')
