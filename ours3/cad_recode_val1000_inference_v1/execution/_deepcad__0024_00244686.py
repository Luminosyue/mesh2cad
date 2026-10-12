import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-84,0,0))
w1=cq.Workplane('XY',origin=(0,0,-56))
r=w0.sketch().segment((-100,-48),(-76,-48)).arc((-35,-45),(4,-27)).segment((63,-27)).segment((63,2)).segment((100,1)).segment((100,57)).segment((26,57)).segment((26,29)).segment((4,29)).arc((-35,56),(-76,48)).segment((-100,48)).close().assemble().finalize().extrude(-3).union(w0.sketch().segment((-98,-2),(-98,2)).segment((-17,2)).segment((-17,-1)).segment((-97,-1)).arc((-78,-15),(-57,-19)).segment((-57,-2)).close().assemble().reset().face(w0.sketch().arc((-27,-55),(-7,-58),(9,-50)).arc((91,-23),(26,36)).arc((10,55),(-12,65)).segment((-12,-55)).close().assemble()).finalize().extrude(56)).union(w1.sketch().segment((-31,-93),(-13,-93)).segment((-13,-65)).segment((11,-65)).segment((11,-33)).segment((43,-33)).segment((43,-28)).segment((84,-28)).segment((84,-27)).segment((43,-27)).segment((43,-23)).arc((68,-1),(79,29)).arc((40,31),(62,62)).arc((44,78),(20,82)).segment((20,100)).segment((-19,100)).segment((-19,81)).segment((-31,81)).segment((-31,63)).arc((-20,43),(-31,23)).segment((-31,10)).arc((-28,0),(-31,-10)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00244686.step')
