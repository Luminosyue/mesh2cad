import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('YZ',origin=(-2,0,0))
r=w0.sketch().arc((-2,-1),(2,0),(-2,1)).segment((-1,1)).segment((-1,-1)).close().assemble().finalize().extrude(200).union(w1.sketch().arc((-1,-96),(2,-73),(-1,-50)).close().assemble().finalize().extrude(4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00306646.step')
