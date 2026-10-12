import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-59,0))
r=w0.sketch().arc((-93,-100),(-32,-85),(25,-100)).segment((93,-100)).segment((93,100)).segment((-93,100)).close().assemble().finalize().extrude(108).union(w0.sketch().segment((-93,-46),(-81,-46)).arc((-19,-32),(32,-70)).segment((93,-70)).segment((93,70)).segment((-93,70)).close().assemble().push([(29,44)]).circle(15,mode='s').finalize().extrude(118))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0013_00130851.step')
