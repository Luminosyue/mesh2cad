import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-100,-6),(-98,-6)).arc((-96,-7),(-94,-6)).segment((-92,-6)).segment((-92,-4)).segment((-94,-4)).arc((-96,-3),(-98,-4)).segment((-100,-4)).close().assemble().reset().face(w0.sketch().segment((-93,-6),(-67,-6)).arc((-60,-7),(-53,-6)).segment((16,-6)).arc((15,-3),(14,-1)).segment((100,-7)).segment((100,6)).segment((14,6)).arc((15,3),(16,1)).segment((-53,1)).arc((-60,3),(-67,1)).segment((-68,1)).segment((-68,-1)).segment((-67,-1)).arc((-69,-3),(-69,-4)).segment((-93,-4)).close().assemble()).reset().face(w0.sketch().segment((23,-2),(25,-2)).arc((26,-3),(28,-2)).segment((30,-2)).segment((30,2)).segment((28,2)).arc((26,3),(25,2)).segment((23,2)).close().assemble(),mode='s').finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00855495.step')
