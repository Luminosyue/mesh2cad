import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-100,-75),(-57,-75)).segment((-57,-74)).segment((-55,-74)).segment((-55,-75)).segment((93,-75)).segment((93,-45)).segment((100,-45)).segment((100,-30)).arc((43,-36),(9,6)).segment((-7,6)).segment((-7,-27)).segment((-13,-27)).segment((-13,6)).segment((-32,6)).segment((-32,25)).segment((-100,25)).close().assemble().reset().face(w0.sketch().segment((-34,-75),(15,-75)).segment((15,-30)).segment((-7,-30)).segment((-7,-74)).segment((-34,-74)).close().assemble(),mode='s').finalize().extrude(-42).union(w0.sketch().push([(-66,-25)]).rect(68,60).push([(-66,-25.5)]).rect(48,21,mode='s').finalize().extrude(-42)).union(w0.sketch().segment((0,-25),(100,-25)).segment((100,60)).segment((83,60)).segment((83,75)).segment((0,75)).segment((0,19)).arc((1,18),(0,17)).close().assemble().push([(49,25)]).circle(33,mode='s').finalize().extrude(42))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00129389.step')
