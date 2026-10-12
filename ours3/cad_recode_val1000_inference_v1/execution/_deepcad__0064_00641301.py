import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,66,0))
w1=cq.Workplane('ZX',origin=(0,16,0))
r=w0.sketch().arc((-93,22),(-96,-18),(-64,-42)).close().assemble().reset().face(w0.sketch().segment((-78,20),(-10,29)).arc((-45,39),(-78,20)).assemble()).reset().face(w0.sketch().arc((-53,-42),(-20,-34),(13,-21)).close().assemble()).reset().face(w0.sketch().segment((-2,30),(50,34)).arc((24,36),(-2,30)).assemble()).reset().face(w0.sketch().arc((12,-22),(37,-24),(59,-34)).segment((65,-42)).segment((68,-41)).segment((26,36)).close().assemble()).reset().face(w0.sketch().segment((45,34),(50,34)).segment((50,42)).arc((48,38),(45,34)).assemble()).finalize().extrude(-132).union(w0.sketch().push([(-68,-34)]).circle(10).push([(63,0)]).circle(37).circle(28,mode='s').finalize().extrude(-51)).union(w1.sketch().arc((-100,1),(-98,-10),(-93,-21)).arc((-86,-10),(-75,-4)).arc((-38,21),(-78,3)).arc((-88,4),(-97,0)).arc((-98,1),(-100,1)).assemble().finalize().extrude(-44))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00641301.step')
