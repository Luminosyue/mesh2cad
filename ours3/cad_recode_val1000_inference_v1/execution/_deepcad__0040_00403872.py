import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-67,-100),(67,-100)).segment((67,91)).arc((20,54),(-3,100)).segment((-67,100)).close().assemble().finalize().extrude(114).union(w0.sketch().segment((-67,-98),(-47,-98)).segment((-47,-100)).segment((67,-100)).segment((67,100)).segment((-67,100)).segment((-67,82)).arc((-30,43),(-67,4)).close().assemble().push([(29,-17)]).circle(32,mode='s').finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00403872.step')
