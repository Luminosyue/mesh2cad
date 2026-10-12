import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-29,0))
r=w0.sketch().segment((-62,38),(-28,-90)).segment((62,-67)).segment((28,65)).close().assemble().push([(0,-12)]).circle(21,mode='s').finalize().extrude(-1).union(w0.sketch().segment((-67,-100),(67,-100)).segment((67,100)).segment((-67,100)).segment((-67,-15)).segment((-19,24)).segment((67,-50)).segment((67,100)).segment((-67,100)).close().assemble().finalize().extrude(59))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00333229.step')
