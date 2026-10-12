import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-22,0))
r=w0.sketch().segment((-55,-88),(55,-88)).segment((55,-24)).segment((50,-24)).arc((-24,-28),(19,30)).segment((19,62)).segment((-55,62)).close().assemble().finalize().extrude(4).union(w0.sketch().segment((-55,-100),(55,-100)).segment((55,-45)).arc((48,-51),(40,-55)).segment((40,-83)).segment((35,-83)).segment((35,-56)).arc((-12,10),(55,53)).segment((55,100)).segment((-55,100)).segment((-55,-2)).arc((-53,-3),(-55,-4)).close().assemble().finalize().extrude(45))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00568426.step')
