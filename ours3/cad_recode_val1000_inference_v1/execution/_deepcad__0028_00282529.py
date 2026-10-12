import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().arc((-2,-100),(2,0),(2,100)).segment((-2,100)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0028_00282529.step')
