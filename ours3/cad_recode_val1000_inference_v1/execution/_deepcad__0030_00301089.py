import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-100,3),(-96,-13)).segment((-81,-9)).segment((-81,-20)).segment((-38,-20)).arc((-42,-13),(-43,-5)).segment((-71,-5)).segment((-71,7)).segment((-40,7)).arc((-39,13),(-37,18)).segment((-43,18)).segment((-43,20)).segment((-81,20)).segment((-81,10)).segment((-98,10)).segment((-98,3)).close().assemble().reset().face(w0.sketch().segment((-43,-20),(83,-20)).segment((83,-19)).arc((100,1),(83,20)).segment((-43,20)).arc((-39,13),(-37,7)).segment((1,7)).arc((2,13),(4,18)).segment((-37,18)).arc((-39,13),(-43,8)).close().assemble()).push([(80,0)]).circle(10,mode='s').finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00301089.step')
