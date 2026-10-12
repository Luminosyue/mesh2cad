import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,60))
r=w0.sketch().segment((-100,-60),(100,-60)).segment((100,60)).segment((-93,60)).arc((-92,48),(-100,38)).close().assemble().push([(-6,-4)]).circle(53,mode='s').finalize().extrude(-120).union(w0.sketch().segment((-83,-52),(100,-52)).segment((100,52)).segment((53,52)).arc((20,30),(-13,52)).segment((-83,52)).close().assemble().finalize().extrude(-93))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00520734.step')
