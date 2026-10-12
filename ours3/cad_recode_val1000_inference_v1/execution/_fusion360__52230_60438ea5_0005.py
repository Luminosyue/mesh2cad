import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,-50))
r=w0.workplane(offset=-108/2).cylinder(108,17).union(w0.sketch().arc((-83,7),(-76,-34),(-56,-66)).segment((-56,-64)).segment((-52,-64)).segment((-52,-67)).arc((-35,-75),(-18,-82)).arc((11,-82),(40,-73)).segment((40,-72)).segment((42,-72)).arc((64,-54),(80,-29)).segment((83,-29)).segment((83,12)).segment((83,13)).segment((83,14)).segment((83,15)).segment((80,15)).arc((64,53),(30,77)).arc((17,82),(3,83)).arc((-47,69),(-80,27)).segment((-83,27)).close().assemble().push([(0,-17)]).circle(44,mode='s').finalize().extrude(-50)).union(w1.sketch().arc((-58,60),(-83,-5),(-38,-66)).segment((-38,-74)).segment((-20,-74)).arc((0,-83),(20,-74)).segment((38,-74)).segment((38,-66)).arc((59,-51),(74,-31)).arc((49,-14),(83,-8)).arc((76,37),(47,68)).arc((4,83),(-40,73)).arc((-43,71),(-46,69)).arc((-49,67),(-51,65)).arc((-54,64),(-58,60)).assemble().finalize().extrude(-50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__52230_60438ea5_0005.step')
