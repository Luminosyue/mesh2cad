import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(86,0,0))
w1=cq.Workplane('YZ',origin=(44,0,0))
r=w0.sketch().arc((-84,51),(-99,-7),(-77,-62)).close().assemble().reset().face(w0.sketch().segment((-57,80),(63,77)).arc((11,98),(-42,90)).arc((-44,67),(-57,80)).assemble()).reset().face(w0.sketch().arc((-54,-82),(-12,-98),(34,-93)).close().assemble()).reset().face(w0.sketch().segment((73,67),(85,-50)).arc((99,8),(73,67)).assemble()).finalize().extrude(-162).union(w0.sketch().push([(-9,0)]).circle(43).circle(33,mode='s').finalize().extrude(-149)).union(w1.sketch().arc((24,-34),(40,-14),(41,11)).arc((-36,21),(24,-34)).assemble().finalize().extrude(-79))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00683791.step')
