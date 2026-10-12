import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-64,0))
r=w0.sketch().segment((-95,-100),(86,-100)).segment((86,-83)).segment((95,-83)).segment((95,100)).segment((-95,100)).segment((-95,-28)).arc((-91,-29),(-95,-30)).close().assemble().push([(-74,82)]).circle(18,mode='s').push([(15,-19)]).circle(47,mode='s').finalize().extrude(128)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00976765.step')
