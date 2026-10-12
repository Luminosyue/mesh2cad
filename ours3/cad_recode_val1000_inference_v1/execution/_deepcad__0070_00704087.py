import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-6,0))
r=w0.sketch().segment((-13,-84),(-4,-96)).segment((6,-100)).segment((5,-91)).segment((-4,-91)).segment((-4,62)).segment((-13,62)).close().assemble().reset().face(w0.sketch().segment((-13,75),(-4,75)).segment((-4,96)).segment((-13,87)).close().assemble()).reset().face(w0.sketch().segment((-9,97),(-4,97)).segment((-4,100)).close().assemble()).finalize().extrude(12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0070_00704087.step')
