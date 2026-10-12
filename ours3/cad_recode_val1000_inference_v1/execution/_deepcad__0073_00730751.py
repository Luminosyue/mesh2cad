import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('YZ',origin=(2,0,0))
r=w0.workplane(offset=200/2).cylinder(200,2).union(w1.sketch().arc((-2,-90),(2,-79),(-2,-67)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00730751.step')
