import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-32))
r=w0.sketch().segment((-24,-97),(19,-97)).segment((19,-50)).segment((-24,-65)).close().assemble().reset().face(w0.sketch().segment((-24,10),(19,-5)).segment((19,10)).segment((-24,39)).close().assemble()).finalize().extrude(51).union(w0.sketch().segment((-24,-100),(24,-100)).segment((24,92)).segment((21,92)).segment((21,100)).segment((-21,100)).segment((-21,92)).segment((-24,92)).segment((-24,16)).arc((-10,18),(-2,5)).arc((-10,-16),(-24,-33)).close().assemble().reset().face(w0.sketch().segment((-24,-32),(-24,-29)).arc((-25,-30),(-24,-32)).assemble(),mode='s').reset().face(w0.sketch().arc((21,-32),(22,-30),(21,-29)).close().assemble(),mode='s').finalize().extrude(64))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0090_00900718.step')
