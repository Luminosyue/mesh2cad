import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-86))
w1=cq.Workplane('ZX',origin=(0,-96,0))
r=w0.sketch().segment((-100,-96),(100,-96)).segment((100,96)).segment((77,96)).arc((1,-18),(-100,76)).close().assemble().finalize().extrude(82).union(w0.sketch().arc((-33,-83),(-29,-66),(-33,-49)).close().assemble().reset().face(w0.sketch().arc((-33,-39),(-31,-34),(-28,-29)).segment((-33,-29)).close().assemble()).reset().face(w0.sketch().arc((31,-29),(33,-34),(35,-39)).segment((35,-29)).close().assemble()).reset().face(w0.sketch().segment((31,56),(35,56)).segment((35,60)).arc((33,55),(31,56)).assemble()).reset().face(w0.sketch().arc((31,77),(33,74),(35,69)).segment((35,77)).close().assemble()).finalize().extrude(172)).union(w1.workplane(offset=192/2).moveTo(-35.5,0).box(101,200,192))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00270881.step')
