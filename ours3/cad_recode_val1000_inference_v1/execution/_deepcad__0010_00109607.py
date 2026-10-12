import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-50))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,60)).segment((15,47)).segment((15,46)).arc((50,10),(31,-38)).segment((31,-41)).segment((28,-41)).arc((-19,-65),(-66,-41)).segment((-70,-41)).segment((-70,-38)).arc((-86,-20),(-100,-1)).close().assemble().finalize().extrude(100).union(w0.sketch().segment((-100,100),(-10,-100)).segment((100,-100)).segment((100,100)).close().assemble().circle(50,mode='s').finalize().extrude(100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00109607.step')
