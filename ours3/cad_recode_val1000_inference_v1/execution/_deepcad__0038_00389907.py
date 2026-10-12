import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,60))
r=w0.sketch().segment((-100,-60),(100,-60)).segment((100,60)).segment((-93,60)).arc((-94,48),(-100,37)).close().assemble().push([(-7,-4)]).circle(50,mode='s').finalize().extrude(-120).union(w0.sketch().segment((-83,45),(-79,45)).arc((-79,47),(-78,49)).segment((-83,49)).close().assemble().reset().face(w0.sketch().arc((-70,56),(-68,55),(-67,53)).segment((-67,56)).close().assemble()).reset().face(w0.sketch().segment((-6,-53),(100,-53)).segment((100,53)).segment((53,53)).arc((37,25),(11,5)).arc((10,-33),(-6,-65)).close().assemble()).finalize().extrude(-93))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00389907.step')
