import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-60,0))
r=w0.sketch().segment((-78,-72),(-54,-72)).segment((-54,-55)).arc((-66,-56),(-78,-55)).close().assemble().reset().face(w0.sketch().arc((-22,69),(-11,69),(-1,67)).segment((-1,73)).segment((-22,73)).close().assemble()).finalize().extrude(10).union(w0.sketch().arc((-100,-74),(-98,-79),(-96,-84)).segment((100,-84)).segment((100,-42)).segment((50,-42)).segment((50,-38)).arc((32,-14),(32,16)).segment((-6,-15)).segment((-13,-6)).segment((-7,1)).arc((-10,6),(-11,11)).segment((-12,12)).segment((-10,13)).arc((-10,14),(-9,14)).segment((10,84)).segment((-100,84)).close().assemble().reset().face(w0.sketch().segment((-54,84),(100,42)).segment((100,84)).close().assemble()).finalize().extrude(120))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00613968.step')
