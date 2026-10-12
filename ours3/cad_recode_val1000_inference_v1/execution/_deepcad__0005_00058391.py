import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().push([(-91,42)]).circle(9).circle(2,mode='s').reset().face(w0.sketch().segment((-94,-18),(-90,-40)).segment((-75,-36)).segment((-79,-14)).close().assemble()).reset().face(w0.sketch().segment((-76,-1),(-72,-10)).segment((-64,-11)).segment((-68,-8)).segment((-68,-9)).segment((-70,-9)).segment((-70,-7)).segment((-76,-1)).close().assemble()).reset().face(w0.sketch().arc((10,-4),(-11,-40),(29,-30)).arc((28,-18),(23,-9)).segment((23,-12)).arc((17,-9),(10,-4)).assemble()).reset().face(w0.sketch().segment((13,-28),(14,-28)).arc((14,-27),(13,-27)).close().assemble(),mode='s').reset().face(w0.sketch().arc((13,-14),(14,-14),(14,-13)).segment((13,-13)).close().assemble(),mode='s').push([(87,-27)]).circle(13).circle(4,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00058391.step')
