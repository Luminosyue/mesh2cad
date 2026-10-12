import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(0,0,0))
r=w0.sketch().segment((-100,21),(-89,-27)).segment((-51,-19)).arc((-30,-27),(-10,-19)).arc((1,-22),(12,-21)).segment((-1,-16)).segment((10,3)).segment((23,-23)).arc((37,-26),(49,-19)).arc((68,-26),(86,-19)).segment((86,-22)).segment((95,-22)).segment((95,-11)).arc((100,2),(97,15)).segment((97,27)).segment((88,27)).arc((82,28),(76,27)).segment((66,27)).segment((66,25)).arc((58,24),(51,21)).arc((20,25),(-5,5)).segment((-17,27)).segment((-55,27)).segment((-55,14)).segment((-57,13)).segment((-82,27)).close().assemble().push([(20,0)]).circle(14,mode='s').finalize().extrude(1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00910820.step')
