import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-67,-74),(-57,-74)).segment((-57,-100)).segment((67,-100)).segment((67,-33)).segment((33,-33)).segment((33,100)).segment((-67,100)).close().assemble().reset().face(w0.sketch().segment((-57,-60),(-57,-33)).segment((-1,-33)).arc((-45,-1),(-57,-60)).assemble(),mode='s').finalize().extrude(134).union(w0.sketch().segment((-67,-100),(67,-100)).segment((67,-48)).arc((50,-39),(36,-27)).arc((-17,-13),(33,10)).arc((33,29),(37,47)).segment((14,47)).segment((14,45)).segment((12,45)).segment((12,47)).segment((-67,47)).close().assemble().reset().face(w0.sketch().segment((-67,66),(-60,66)).arc((-58,68),(-56,69)).segment((-67,69)).close().assemble()).finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0028_00284228.step')
