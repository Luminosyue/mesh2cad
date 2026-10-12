import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(6,0,0))
r=w0.sketch().segment((-100,-100),(-58,-100)).segment((-58,-73)).segment((-100,-10)).close().assemble().reset().face(w0.sketch().segment((-100,34),(-58,-44)).segment((-58,-43)).segment((-10,-43)).segment((-10,-100)).segment((100,-100)).segment((100,67)).segment((86,67)).segment((86,96)).segment((70,96)).segment((70,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-96,34),(-78,34)).segment((-78,4)).segment((-47,4)).segment((-47,34)).segment((-29,34)).segment((-29,46)).segment((-47,46)).segment((-47,76)).segment((-78,76)).segment((-78,46)).segment((-96,46)).close().assemble(),mode='s').push([(29,38)]).circle(22,mode='s').reset().face(w0.sketch().segment((-27,0),(-10,-48)).segment((92,-15)).segment((75,33)).close().assemble()).finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__23649_45d06d26_0002.step')
