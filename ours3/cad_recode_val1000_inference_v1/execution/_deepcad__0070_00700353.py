import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.workplane(offset=-200/2).cylinder(200,13).union(w1.sketch().arc((-11,-6),(11,6),(-10,-8)).segment((-5,-8)).segment((-5,-6)).close().assemble().finalize().extrude(-152))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0070_00700353.step')
