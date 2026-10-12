import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-7))
r=w0.sketch().segment((-100,-67),(-43,-67)).segment((-43,-60)).arc((-36,-60),(-29,-59)).segment((-29,-67)).segment((32,-67)).segment((32,-66)).segment((100,-66)).segment((100,-39)).arc((88,-48),(74,-54)).segment((74,-61)).segment((58,-61)).segment((58,-54)).arc((44,-48),(32,-39)).segment((32,-37)).arc((44,-23),(58,-16)).segment((58,-9)).segment((74,-9)).segment((74,-16)).arc((88,-23),(100,-37)).segment((100,62)).segment((82,62)).segment((82,67)).segment((14,67)).segment((14,62)).segment((-24,62)).segment((-24,51)).arc((-58,55),(-87,40)).segment((-87,67)).segment((-100,67)).segment((-100,36)).segment((-87,36)).segment((-87,-13)).segment((-100,-13)).close().assemble().reset().face(w0.sketch().segment((-81,24),(-13,-39)).segment((51,19)).segment((-17,69)).close().assemble(),mode='s').push([(76,38)]).circle(9,mode='s').finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00384130.step')
