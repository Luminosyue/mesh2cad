import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
r=w0.sketch().segment((-32,-65),(-31,-65)).arc((1,-100),(31,-65)).segment((32,-65)).segment((32,100)).segment((22,98)).segment((31,98)).segment((31,78)).segment((10,100)).segment((-24,68)).segment((14,27)).segment((-11,27)).segment((-11,45)).segment((-32,45)).segment((-32,-10)).segment((-29,-10)).segment((-32,-19)).close().assemble().push([(0,-68)]).circle(14,mode='s').reset().face(w0.sketch().segment((-11,-10),(15,-25)).segment((32,-25)).segment((32,11)).segment((-11,1)).close().assemble(),mode='s').finalize().extrude(-24)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00806885.step')
