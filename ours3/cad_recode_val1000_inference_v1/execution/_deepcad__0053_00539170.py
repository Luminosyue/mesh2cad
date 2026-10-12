import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,33,0))
w1=cq.Workplane('ZX',origin=(0,17,0))
r=w0.sketch().segment((-87,-45),(-71,-45)).segment((-71,-16)).segment((-37,-45)).segment((-15,-45)).segment((-15,-70)).segment((-50,-70)).segment((0,-100)).segment((20,-70)).segment((22,-70)).segment((22,-86)).segment((87,-45)).segment((87,49)).segment((0,100)).segment((-20,70)).segment((-22,70)).segment((-22,86)).segment((-87,45)).close().assemble().push([(0,-1)]).circle(17,mode='s').finalize().extrude(-66).union(w1.sketch().arc((-83,52),(-78,48),(-73,45)).arc((61,-65),(-55,64)).arc((-69,61),(-83,52)).assemble().finalize().extrude(-39))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00539170.step')
