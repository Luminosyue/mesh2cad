import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,50))
w1=cq.Workplane('YZ',origin=(20,0,0))
r=w0.sketch().segment((-100,-60),(-89,-60)).segment((-93,-41)).segment((-78,-38)).arc((-78,-20),(-86,-5)).segment((-86,-10)).segment((-88,-10)).segment((-88,-4)).arc((-93,13),(-88,30)).segment((-88,39)).segment((-86,39)).segment((-86,30)).arc((-79,27),(-73,22)).segment((-60,37)).segment((-60,39)).segment((-58,39)).segment((-58,37)).segment((-23,39)).segment((-31,60)).segment((-100,60)).close().assemble().reset().face(w0.sketch().segment((-20,-60),(100,-60)).segment((100,-32)).arc((74,-48),(43,-41)).segment((43,-56)).segment((10,-56)).segment((10,-41)).arc((-5,-43),(-20,-41)).close().assemble()).reset().face(w0.sketch().arc((10,4),(26,12),(43,1)).segment((43,29)).segment((100,29)).segment((100,60)).segment((43,60)).segment((43,56)).segment((10,56)).close().assemble()).finalize().extrude(-90).union(w1.sketch().segment((-56,-50),(38,-50)).arc((54,-15),(20,5)).arc((-10,44),(-10,-5)).arc((-16,-25),(-5,-44)).arc((-31,-45),(-56,-36)).close().assemble().push([(19,30)]).rect(16,10,mode='s').finalize().extrude(29))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00763570.step')
