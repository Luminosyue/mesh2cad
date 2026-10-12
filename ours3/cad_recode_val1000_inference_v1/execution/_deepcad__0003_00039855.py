import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-36))
w1=cq.Workplane('YZ',origin=(-54,0,0))
r=w0.sketch().segment((-80,-72),(-48,-72)).segment((-48,-67)).arc((-61,-58),(-70,-45)).segment((-80,-69)).close().assemble().reset().face(w0.sketch().segment((-80,-22),(-19,-22)).arc((-20,-23),(-20,-24)).segment((-19,-24)).segment((-19,-25)).arc((-10,-43),(-19,-61)).segment((-19,-62)).arc((10,-69),(18,-40)).segment((23,-40)).segment((23,24)).segment((-29,24)).segment((-29,56)).segment((-32,56)).segment((-31,24)).segment((-100,24)).segment((-100,-15)).arc((-90,-17),(-80,-14)).close().assemble()).push([(77,2)]).rect(46,64).finalize().extrude(29).union(w0.sketch().push([(77,2)]).rect(46,110).push([(77,1.5)]).rect(42,55,mode='s').finalize().extrude(72)).union(w1.sketch().segment((-38,-12),(-10,-12)).segment((-10,30)).segment((-29,30)).segment((-29,36)).segment((-10,36)).segment((-10,37)).segment((-38,37)).close().assemble().push([(43.5,0)]).rect(29,60).finalize().extrude(-46))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0003_00039855.step')
