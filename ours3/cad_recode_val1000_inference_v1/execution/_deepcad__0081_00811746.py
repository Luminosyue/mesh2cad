import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,50,0))
w1=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-33,-100),(33,-100)).segment((33,-44)).arc((27,-45),(21,-45)).segment((21,-54)).segment((-21,-54)).segment((-21,-45)).arc((-27,-45),(-33,-44)).close().assemble().reset().face(w0.sketch().arc((-33,44),(-27,45),(-21,45)).segment((-21,54)).segment((0,54)).segment((0,0)).segment((33,0)).segment((33,-18)).arc((31,-5),(26,7)).arc((26,6),(25,6)).segment((25,0)).segment((0,0)).segment((0,6)).arc((-1,6),(-1,7)).arc((-1,8),(-2,8)).arc((-1,14),(0,20)).segment((0,100)).segment((-33,100)).close().assemble()).finalize().extrude(-100).union(w1.sketch().push([(14,0)]).circle(50).circle(40,mode='s').finalize().extrude(-33))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00811746.step')
