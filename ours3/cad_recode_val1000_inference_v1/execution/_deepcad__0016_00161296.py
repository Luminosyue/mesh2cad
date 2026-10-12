import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-5,-100),(5,-100)).segment((5,61)).segment((5,100)).segment((-5,100)).segment((-5,-34)).segment((-2,-34)).segment((-2,-37)).segment((-5,-37)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00161296.step')
