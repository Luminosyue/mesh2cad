import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(93,0,0))
r=w0.workplane(offset=-200/2).moveTo(-4,0).cylinder(200,18).union(w0.workplane(offset=-35/2).moveTo(0,1).cylinder(35,21)).union(w1.sketch().arc((-15,16),(13,-17),(-12,19)).arc((-12,16),(-15,16)).assemble().finalize().extrude(-153))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00759575.step')
