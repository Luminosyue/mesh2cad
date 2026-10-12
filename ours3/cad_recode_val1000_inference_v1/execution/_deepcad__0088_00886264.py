import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-3,0))
r=w0.sketch().push([(0,-88)]).circle(12).push([(0,88)]).circle(12).finalize().extrude(6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00886264.step')
