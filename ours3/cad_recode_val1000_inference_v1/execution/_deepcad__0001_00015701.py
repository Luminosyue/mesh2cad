import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,40))
w1=cq.Workplane('XY',origin=(0,0,11))
r=w0.sketch().segment((-78,-61),(-46,-88)).segment((-42,-83)).arc((-33,-93),(-21,-96)).arc((33,-93),(75,-64)).arc((50,-55),(30,-37)).arc((-35,5),(35,3)).arc((62,51),(72,95)).arc((-71,70),(-74,-66)).close().assemble().finalize().extrude(-80).union(w0.sketch().arc((-92,-39),(-14,-97),(72,-69)).arc((10,-41),(-35,10)).segment((-35,-10)).segment((-63,-10)).segment((-63,20)).segment((-37,20)).arc((21,59),(91,39)).arc((86,48),(80,56)).arc((69,67),(60,79)).arc((47,86),(33,90)).arc((10,91),(-12,88)).arc((-84,51),(-92,-39)).assemble().finalize().extrude(-48)).union(w1.workplane(offset=-28/2).moveTo(0,-1).cylinder(28,35))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0001_00015701.step')
