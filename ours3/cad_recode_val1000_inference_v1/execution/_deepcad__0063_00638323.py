import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,36,0))
w1=cq.Workplane('YZ',origin=(14,0,0))
r=w0.sketch().segment((-50,-100),(36,-100)).segment((36,-10)).segment((36,43)).segment((36,100)).segment((-50,100)).segment((-50,75)).arc((-46,73),(-43,70)).arc((-48,58),(-50,43)).segment((-50,-43)).segment((-50,-100)).assemble().reset().face(w0.sketch().arc((-29,1),(-26,-4),(-22,-8)).arc((-18,-10),(-15,-12)).arc((1,-57),(36,-26)).arc((10,57),(-29,1)).assemble(),mode='s').reset().face(w0.sketch().arc((-50,75),(-29,83),(-8,83)).segment((-8,99)).segment((-18,99)).segment((-18,91)).arc((-35,91),(-50,85)).close().assemble(),mode='s').finalize().extrude(-86).union(w1.sketch().segment((37,45),(49,45)).arc((43,50),(37,45)).assemble().finalize().extrude(26))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0063_00638323.step')
