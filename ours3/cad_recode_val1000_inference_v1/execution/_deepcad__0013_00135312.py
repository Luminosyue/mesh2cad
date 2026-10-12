import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-77,0))
w1=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.sketch().segment((-100,-71),(96,-71)).segment((96,-30)).segment((100,-30)).segment((100,71)).segment((-100,71)).segment((-100,39)).arc((-95,30),(-100,21)).close().assemble().push([(17,0)]).circle(7,mode='s').push([(56,70)]).circle(2,mode='s').finalize().extrude(154).union(w1.sketch().segment((-20,-6),(-16,-6)).segment((-16,-23)).segment((63,-23)).segment((63,61)).segment((-16,61)).segment((-16,18)).segment((-20,18)).close().assemble().finalize().extrude(16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0013_00135312.step')
