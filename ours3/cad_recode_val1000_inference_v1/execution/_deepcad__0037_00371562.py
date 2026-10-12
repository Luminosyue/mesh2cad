import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,36,0))
r=w0.sketch().segment((-55,-100),(55,-100)).segment((55,-27)).segment((-18,-27)).segment((-18,31)).segment((-19,31)).segment((-19,41)).segment((-18,41)).segment((-18,77)).segment((-20,77)).segment((-20,83)).segment((-18,83)).segment((-18,100)).segment((-55,100)).segment((-55,83)).segment((-55,77)).segment((-55,41)).segment((-55,31)).segment((-55,-27)).close().assemble().reset().face(w0.sketch().segment((-55,-68),(-54,-68)).arc((-37,-77),(-20,-68)).segment((-19,-68)).segment((-19,-66)).arc((-18,-61),(-19,-56)).segment((-19,-54)).segment((-20,-54)).arc((-37,-45),(-54,-54)).segment((-55,-54)).segment((-55,-56)).arc((-56,-61),(-55,-66)).close().assemble(),mode='s').push([(47,-92)]).circle(4,mode='s').finalize().extrude(-72).union(w0.sketch().arc((-49,-48),(-47,-53),(-44,-57)).segment((-44,-89)).segment((45,-89)).segment((45,-75)).arc((32,-51),(45,-27)).segment((-44,-27)).segment((-44,-48)).close().assemble().finalize().extrude(-2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00371562.step')
