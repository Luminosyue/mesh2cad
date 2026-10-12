import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-80,0))
r=w0.sketch().segment((-100,-76),(100,-76)).segment((100,76)).segment((-100,76)).segment((-100,42)).arc((-91,48),(-81,52)).arc((-70,68),(-53,76)).segment((-100,76)).close().assemble().reset().face(w0.sketch().arc((-52,-76),(0,-80),(52,-76)).segment((-12,-76)).arc((-13,-77),(-14,-76)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-52,76),(12,76)).arc((0,80),(-14,76)).segment((-52,76)).assemble(),mode='s').finalize().extrude(160)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0084_00844916.step')
