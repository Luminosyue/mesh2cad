import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(40,0,0))
r=w0.sketch().segment((-100,-84),(-64,-84)).arc((-45,-47),(-27,-84)).segment((100,-84)).segment((100,84)).segment((-100,84)).close().assemble().reset().face(w0.sketch().arc((-88,-42),(-86,-45),(-83,-47)).arc((15,-39),(10,58)).arc((1,74),(-15,84)).segment((-15,85)).segment((-88,85)).segment((-88,84)).segment((-15,84)).segment((-15,83)).arc((-84,44),(-88,-37)).close().assemble(),mode='s').reset().face(w0.sketch().arc((22,-84),(34,-85),(46,-84)).close().assemble(),mode='s').reset().face(w0.sketch().segment((22,84),(46,84)).arc((34,85),(22,84)).assemble(),mode='s').reset().face(w0.sketch().arc((50,-83),(72,-60),(86,-32)).arc((68,-58),(50,-83)).assemble(),mode='s').finalize().extrude(-80).union(w0.sketch().arc((-20,-64),(11,-16),(68,-11)).arc((78,15),(89,42)).arc((76,53),(68,64)).arc((-49,37),(-20,-64)).assemble().finalize().extrude(-2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00363332.step')
