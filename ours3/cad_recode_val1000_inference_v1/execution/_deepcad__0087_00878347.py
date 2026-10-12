import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,82))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-60,-15),(-58,-23),(-55,-29)).arc((-45,-43),(-32,-53)).close().assemble().reset().face(w0.sketch().arc((-45,44),(-37,47),(-28,49)).segment((-28,55)).segment((-14,55)).segment((-14,60)).arc((22,24),(26,-24)).segment((45,-44)).arc((43,44),(-45,44)).assemble()).reset().face(w0.sketch().arc((-10,-44),(1,-47),(13,-49)).segment((14,-49)).segment((14,-48)).arc((20,-47),(26,-44)).close().assemble()).finalize().extrude(-182).union(w1.sketch().arc((-47,41),(-62,-5),(-31,-45)).arc((-26,-20),(-18,-45)).arc((12,-60),(44,-45)).arc((43,-40),(47,-41)).arc((57,26),(2,63)).arc((-15,28),(-47,41)).assemble().finalize().extrude(-73))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00878347.step')
