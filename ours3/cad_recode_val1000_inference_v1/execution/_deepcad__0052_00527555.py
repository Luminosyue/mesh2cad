import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,-48)).arc((-96,-52),(-100,-56)).close().assemble().push([(-39,-1)]).circle(10,mode='s').finalize().extrude(-200).union(w0.sketch().segment((-64,-90),(64,-90)).segment((64,-5)).arc((66,1),(64,7)).segment((64,90)).segment((-64,90)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00527555.step')
