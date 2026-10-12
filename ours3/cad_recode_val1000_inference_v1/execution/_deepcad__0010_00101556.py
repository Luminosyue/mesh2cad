import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,62))
w1=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((-85,-62),(8,-62)).segment((8,-8)).segment((-32,-8)).segment((-32,39)).segment((-85,39)).close().assemble().finalize().extrude(-62).union(w0.sketch().segment((-84,-61),(8,-61)).segment((8,12)).segment((18,12)).arc((19,18),(20,24)).segment((10,24)).segment((10,22)).segment((-84,22)).close().assemble().reset().face(w0.sketch().segment((-84,49),(-69,49)).segment((-69,62)).segment((-84,62)).segment((-84,59)).arc((-82,58),(-84,57)).close().assemble()).reset().face(w0.sketch().segment((-28,61),(-27,58)).segment((49,61)).segment((49,62)).close().assemble()).push([(74,30.5)]).rect(52,51).finalize().extrude(-22)).union(w1.sketch().segment((-62,-100),(55,-100)).segment((55,-69)).segment((-53,-69)).segment((-53,-71)).segment((-55,-71)).segment((-55,-69)).segment((-62,-69)).close().assemble().finalize().extrude(83))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00101556.step')
