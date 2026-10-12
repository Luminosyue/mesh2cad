import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
w1=cq.Workplane('XY',origin=(0,0,-7))
r=w0.sketch().segment((-100,-57),(-97,-58)).segment((-97,-72)).segment((-72,-72)).segment((-72,-69)).segment((-35,-69)).segment((-35,-72)).segment((-10,-72)).segment((-10,-69)).segment((15,-69)).segment((15,-61)).segment((92,-72)).segment((100,-4)).segment((87,-2)).segment((94,43)).segment((74,46)).segment((67,10)).segment((32,15)).segment((32,41)).segment((28,41)).segment((28,16)).segment((-10,20)).segment((-10,23)).segment((-35,23)).segment((-35,47)).segment((-97,47)).segment((-97,23)).segment((-100,23)).segment((-100,1)).segment((-97,1)).segment((-97,-2)).segment((-72,-2)).segment((-72,-5)).segment((-99,0)).close().assemble().push([(-52,-29)]).circle(19,mode='s').push([(5,-43)]).circle(25,mode='s').finalize().extrude(3).union(w1.sketch().segment((-99,-15),(-47,-15)).segment((-47,-10)).segment((-73,-10)).segment((-73,17)).segment((-47,17)).segment((-47,63)).segment((-73,63)).segment((-73,65)).segment((-97,65)).segment((-97,63)).segment((-99,63)).segment((-99,32)).arc((-86,11),(-99,-9)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00368831.step')
