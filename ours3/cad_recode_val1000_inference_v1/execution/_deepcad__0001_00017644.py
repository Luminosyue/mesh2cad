import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,20))
r=w0.sketch().push([(-75,-30)]).circle(25).reset().face(w0.sketch().segment((-74,-57),(-63,-54)).segment((-64,-51)).segment((-74,-54)).close().assemble()).reset().face(w0.sketch().arc((32,-14),(45,-17),(55,-8)).arc((59,-11),(63,-13)).arc((61,-14),(60,-16)).segment((56,-16)).segment((56,-18)).segment((60,-18)).arc((63,-22),(68,-23)).arc((59,-51),(86,-54)).segment((88,-54)).segment((88,-53)).arc((93,-50),(97,-45)).segment((88,-45)).segment((88,-43)).segment((98,-43)).arc((96,-18),(74,-8)).arc((64,-10),(63,1)).arc((63,29),(42,50)).segment((42,51)).segment((40,51)).arc((-14,25),(32,-14)).assemble()).finalize().extrude(-40).union(w0.sketch().segment((-100,-33),(-64,-56)).segment((-52,-37)).segment((-88,-14)).close().assemble().reset().face(w0.sketch().segment((1,-15),(42,-23)).segment((44,-15)).arc((64,10),(52,41)).segment((54,49)).segment((13,57)).segment((11,49)).arc((-9,24),(3,-7)).close().assemble()).finalize().extrude(-18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0001_00017644.step')
