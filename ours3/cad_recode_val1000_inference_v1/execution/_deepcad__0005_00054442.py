import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-42,-100),(42,-100)).segment((42,100)).segment((-42,100)).segment((-42,73)).segment((-40,73)).segment((-40,69)).segment((-42,69)).close().assemble().push([(-40,2)]).circle(3,mode='s').push([(0,0)]).circle(3,mode='s').finalize().extrude(200)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00054442.step')
