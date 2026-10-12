import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-5,0))
r=w0.sketch().segment((-13,-88),(-11,-88)).arc((2,-100),(13,-86)).segment((13,54)).segment((2,42)).segment((-13,53)).close().assemble().push([(0,-91)]).circle(4,mode='s').reset().face(w0.sketch().segment((-13,63),(-2,62)).segment((2,99)).segment((-11,100)).close().assemble()).reset().face(w0.sketch().segment((-2,62),(12,61)).segment((13,78)).segment((2,78)).close().assemble()).finalize().extrude(11)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00295360.step')
