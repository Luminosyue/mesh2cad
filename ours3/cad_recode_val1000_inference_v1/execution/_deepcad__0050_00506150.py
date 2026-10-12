import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-100,-67),(-27,-67)).segment((-27,-40)).segment((-10,-40)).segment((-10,-67)).segment((94,-67)).segment((-100,67)).close().assemble().reset().face(w0.sketch().segment((-100,-12),(-100,12)).arc((-100,0),(-100,-12)).assemble()).reset().face(w0.sketch().segment((-99,66),(-95,63)).segment((-94,65)).segment((-98,67)).close().assemble()).reset().face(w0.sketch().segment((-87,28),(-34,-4)).segment((-24,16)).segment((-87,57)).close().assemble()).push([(13,-27)]).circle(15).reset().face(w0.sketch().segment((27,-40),(44,-67)).segment((94,-67)).close().assemble()).finalize().extrude(-16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00506150.step')
