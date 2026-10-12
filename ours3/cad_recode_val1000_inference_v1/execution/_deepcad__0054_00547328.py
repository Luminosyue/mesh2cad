import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().segment((-25,10),(-21,10)).segment((-21,14)).arc((25,55),(-21,96)).segment((-21,100)).segment((-25,100)).segment((-25,96)).arc((-60,55),(-25,14)).close().assemble().finalize().extrude(6).union(w0.sketch().segment((-44,-100),(44,-100)).segment((44,-10)).segment((31,-10)).arc((36,2),(31,14)).segment((44,14)).segment((44,100)).segment((17,100)).arc((20,83),(13,67)).segment((13,65)).segment((12,65)).arc((-14,32),(-12,-10)).segment((-44,-10)).close().assemble().push([(0,-55)]).circle(16,mode='s').reset().face(w0.sketch().segment((-44,40),(-40,67)).segment((-44,67)).close().assemble()).finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0054_00547328.step')
