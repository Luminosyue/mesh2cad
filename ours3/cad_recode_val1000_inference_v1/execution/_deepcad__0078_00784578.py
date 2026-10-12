import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-62,0))
r=w0.sketch().segment((-67,0),(-51,-42)).segment((-51,-37)).segment((51,-37)).segment((51,-11)).segment((67,0)).segment((51,42)).segment((51,37)).segment((-51,37)).segment((-51,11)).close().assemble().finalize().extrude(45).union(w0.sketch().circle(66).circle(65,mode='s').finalize().extrude(155)).union(w1.sketch().arc((-64,15),(14,-64),(45,49)).arc((43,48),(41,47)).arc((39,45),(37,44)).arc((39,37),(39,29)).arc((40,27),(39,25)).arc((39,23),(38,21)).arc((37,19),(37,17)).arc((39,14),(37,11)).arc((36,10),(36,9)).arc((34,8),(32,8)).arc((29,5),(25,3)).arc((21,2),(18,0)).arc((-19,-63),(-61,0)).arc((-63,7),(-64,15)).assemble().finalize().extrude(162))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00784578.step')
