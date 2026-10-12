import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-36,0))
r=w0.sketch().segment((-55,-100),(55,-100)).segment((55,-64)).segment((-18,-64)).segment((-18,66)).segment((-55,66)).segment((-55,-29)).segment((-54,-29)).segment((-54,-31)).segment((-55,-31)).close().assemble().reset().face(w0.sketch().segment((-55,87),(-18,87)).segment((-18,97)).segment((-55,97)).segment((-55,93)).arc((-53,92),(-55,91)).close().assemble()).finalize().extrude(63).union(w0.sketch().segment((-49,-68),(-18,-68)).segment((-18,-93)).segment((46,-93)).segment((46,-64)).segment((-18,-64)).segment((-18,-16)).segment((-49,-16)).close().assemble().reset().face(w0.sketch().segment((-49,-64),(-18,-64)).segment((-18,-68)).segment((-18,-75)).segment((46,-75)).segment((46,-64)).segment((46,-63)).segment((-49,-63)).close().assemble(),mode='s').finalize().extrude(72))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00800294.step')
