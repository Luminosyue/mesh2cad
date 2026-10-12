import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-100,-50),(-50,-50)).segment((-50,-100)).segment((100,-100)).segment((100,-50)).segment((25,-50)).segment((25,50)).segment((100,50)).segment((100,100)).segment((-50,100)).segment((-50,50)).segment((-100,50)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-73,-50),(-50,-50)).segment((-50,-97)).segment((50,-97)).segment((50,-50)).segment((73,-50)).segment((73,50)).segment((50,50)).segment((50,97)).segment((-50,97)).segment((-50,50)).segment((-73,50)).close().assemble().finalize().extrude(-176))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0013_00130675.step')
