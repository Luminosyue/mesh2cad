import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-50))
r=w0.sketch().arc((-67,-73),(25,-95),(96,-25)).segment((57,-25)).arc((0,-77),(-67,-73)).assemble().finalize().extrude(64).union(w0.sketch().segment((-94,-33),(-35,-94)).segment((-19,-76)).arc((79,-59),(87,42)).segment((94,50)).segment((73,67)).arc((65,75),(56,81)).segment((35,94)).segment((33,92)).arc((-74,66),(-87,-38)).close().assemble().reset().face(w0.sketch().segment((-44,-1),(-1,-11)).segment((-10,5)).segment((9,5)).segment((-44,25)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-9,56),(10,39)).segment((10,56)).close().assemble(),mode='s').reset().face(w0.sketch().segment((10,-39),(44,-59)).segment((44,-1)).segment((10,-1)).close().assemble(),mode='s').reset().face(w0.sketch().segment((56,56),(89,36)).segment((90,56)).close().assemble(),mode='s').finalize().extrude(100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0069_00690657.step')
