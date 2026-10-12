import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-100,-79),(-95,-82)).segment((-54,-33)).segment((-54,-48)).segment((-46,-48)).segment((-46,-58)).segment((-42,-58)).segment((-42,-68)).segment((-46,-68)).segment((-46,-71)).segment((-25,-74)).segment((-23,-66)).arc((-21,-68),(-18,-70)).segment((-32,-6)).segment((-36,-12)).segment((-32,-6)).segment((-32,-5)).segment((-31,-5)).segment((-19,17)).segment((-27,8)).segment((17,36)).segment((2,82)).segment((-7,66)).segment((-5,71)).segment((-10,72)).segment((-12,64)).segment((-16,41)).segment((-27,9)).segment((-19,17)).segment((-19,18)).segment((-20,18)).segment((-32,-6)).segment((-32,-5)).close().assemble().reset().face(w0.sketch().arc((-11,-70),(17,-70),(42,-58)).segment((46,-78)).segment((100,-87)).arc((73,-56),(45,-23)).arc((35,-28),(24,-31)).arc((10,-52),(-11,-58)).close().assemble()).finalize().extrude(16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00877007.step')
