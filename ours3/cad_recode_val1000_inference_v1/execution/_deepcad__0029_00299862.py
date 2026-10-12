import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
w1=cq.Workplane('YZ',origin=(-55,0,0))
r=w0.sketch().arc((-7,29),(7,55),(-7,79)).close().assemble().finalize().extrude(-11).union(w0.sketch().arc((-7,-100),(7,-76),(-7,-52)).close().assemble().finalize().extrude(-11)).union(w0.sketch().segment((-55,-42),(-45,-42)).arc((-46,-40),(-45,-37)).segment((-55,-37)).close().assemble().reset().face(w0.sketch().segment((-55,15),(-45,15)).arc((-46,18),(-45,21)).segment((-55,21)).close().assemble()).reset().face(w0.sketch().segment((-43,-42),(-32,-42)).segment((-32,-37)).segment((-43,-37)).arc((-42,-40),(-43,-42)).assemble()).reset().face(w0.sketch().segment((-19,-39),(51,-45)).segment((52,-38)).segment((-18,-33)).close().assemble()).push([(13,-12)]).circle(3).reset().face(w0.sketch().segment((11,45),(55,40)).segment((55,45)).segment((11,45)).close().assemble()).finalize().extrude(7)).union(w1.workplane(offset=74/2).moveTo(3,-1).cylinder(74,4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00299862.step')
