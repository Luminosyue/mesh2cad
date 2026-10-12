import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-91,-31),(-44,-31)).segment((-44,-47)).segment((68,-63)).segment((73,-31)).segment((91,-31)).segment((91,91)).segment((-91,91)).close().assemble().reset().face(w0.sketch().segment((-59,-1),(-44,-1)).segment((-44,1)).segment((59,1)).segment((59,57)).segment((-59,57)).close().assemble(),mode='s').finalize().extrude(10).union(w0.workplane(offset=99/2).moveTo(-28,0).cylinder(99,46)).union(w0.sketch().segment((-91,-91),(91,-91)).segment((91,91)).segment((20,91)).arc((22,89),(24,86)).segment((37,86)).segment((37,81)).segment((25,81)).arc((-28,-34),(-9,89)).arc((-10,90),(-10,91)).segment((-91,91)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00748544.step')
