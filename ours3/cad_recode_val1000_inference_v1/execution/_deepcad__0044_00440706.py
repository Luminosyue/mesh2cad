import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,17))
r=w0.sketch().segment((-81,-100),(-38,-100)).segment((-81,8)).close().assemble().reset().face(w0.sketch().segment((-79,19),(-54,-10)).segment((-54,19)).close().assemble()).reset().face(w0.sketch().segment((-34,52),(49,52)).segment((49,10)).segment((-20,10)).segment((-19,9)).arc((-20,-10),(-12,-28)).segment((-12,-46)).segment((-16,-59)).segment((-12,-60)).segment((-12,-100)).segment((81,-100)).segment((81,52)).segment((76,52)).segment((76,53)).segment((75,52)).segment((-34,52)).close().assemble()).finalize().extrude(-48).union(w0.sketch().segment((-14,43),(23,5)).segment((60,43)).segment((23,79)).close().assemble().push([(71,77)]).circle(4).finalize().extrude(14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00440706.step')
