import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-6,-87),(-1,-100)).segment((6,-94)).segment((5,-94)).segment((5,74)).segment((3,74)).segment((3,97)).segment((-6,100)).segment((-6,74)).segment((-4,74)).segment((-4,-94)).segment((-6,-94)).close().assemble().finalize().extrude(0)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00426089.step')
