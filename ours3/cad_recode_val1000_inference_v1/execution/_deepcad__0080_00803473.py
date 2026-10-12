import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.workplane(offset=-200/2).box(200,200,200).union(w0.sketch().segment((-91,-75),(91,-75)).segment((91,12)).segment((42,12)).segment((42,75)).segment((-91,75)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00803473.step')
