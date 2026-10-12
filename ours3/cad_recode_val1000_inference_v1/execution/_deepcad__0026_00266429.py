import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-100,-7),(-89,-7)).segment((-89,-28)).segment((-78,-28)).segment((-78,-32)).segment((-69,-32)).segment((-69,-28)).segment((-58,-28)).segment((-58,-40)).segment((-19,-40)).arc((-20,-34),(-20,-28)).segment((-10,-28)).segment((-10,-22)).arc((10,-24),(26,-40)).segment((34,-40)).arc((23,-33),(12,-28)).segment((32,-28)).arc((31,-33),(29,-37)).arc((29,-38),(30,-40)).segment((100,-40)).segment((100,40)).segment((55,40)).arc((73,2),(55,-37)).arc((56,-33),(56,-28)).segment((66,-28)).segment((66,-22)).arc((79,0),(89,23)).arc((77,29),(66,37)).segment((66,40)).segment((56,40)).arc((56,38),(55,37)).arc((23,38),(-10,28)).segment((-20,28)).arc((-55,40),(-89,28)).segment((-89,13)).segment((-100,13)).close().assemble().finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00266429.step')
