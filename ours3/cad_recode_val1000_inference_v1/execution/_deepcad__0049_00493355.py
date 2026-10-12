import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-47,0))
r=w0.sketch().segment((-91,-58),(-50,-58)).arc((0,-83),(50,-58)).segment((91,-58)).segment((91,79)).segment((50,79)).arc((0,100),(-50,79)).segment((-91,79)).close().assemble().push([(0,-1)]).circle(33,mode='s').finalize().extrude(1).union(w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,99)).segment((-100,-10)).close().assemble().finalize().extrude(94))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00493355.step')
