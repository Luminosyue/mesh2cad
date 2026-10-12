import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(0,0,0))
r=w0.sketch().segment((-100,50),(-90,48)).segment((-90,50)).segment((-98,51)).arc((-99,48),(-100,50)).assemble().reset().face(w0.sketch().segment((-97,-1),(-80,-22)).segment((-50,-7)).segment((-90,15)).segment((-90,-1)).close().assemble()).reset().face(w0.sketch().segment((-56,-23),(-52,-35)).segment((-44,-32)).arc((-24,-40),(-7,-28)).segment((-18,-24)).segment((-40,-24)).segment((-40,-20)).close().assemble()).reset().face(w0.sketch().segment((-13,-24),(-1,-24)).segment((-12,-22)).close().assemble()).reset().face(w0.sketch().segment((-1,-61),(14,-61)).segment((14,-50)).segment((48,-59)).segment((49,-53)).segment((14,-44)).segment((14,-45)).segment((-1,-45)).close().assemble()).reset().face(w0.sketch().segment((47,27),(100,27)).segment((92,59)).segment((77,56)).arc((54,59),(50,36)).segment((47,36)).close().assemble()).finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00713154.step')
