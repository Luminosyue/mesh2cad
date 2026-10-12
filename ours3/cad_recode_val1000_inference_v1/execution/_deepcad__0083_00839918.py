import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,81))
w1=cq.Workplane('XY',origin=(0,0,27))
r=w0.sketch().arc((-39,-92),(10,97),(33,-94)).segment((33,-88)).arc((10,87),(-39,-83)).close().assemble().finalize().extrude(-162).union(w0.sketch().segment((-100,-3),(-42,9)).arc((-1,45),(45,14)).segment((97,23)).arc((-16,97),(-100,-3)).assemble().reset().face(w0.sketch().arc((-90,-42),(-73,-68),(-48,-86)).close().assemble()).reset().face(w0.sketch().arc((-3,-97),(36,-93),(67,-69)).close().assemble()).finalize().extrude(-37)).union(w1.sketch().arc((-33,-31),(24,37),(94,-17)).arc((97,-18),(98,-20)).arc((99,-21),(100,-21)).arc((24,42),(-33,-31)).assemble().finalize().extrude(-92))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00839918.step')
