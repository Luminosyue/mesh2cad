import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-62,0))
r=w0.sketch().segment((-67,0),(-51,-42)).segment((-51,-37)).segment((51,-37)).segment((51,-11)).segment((67,0)).segment((51,42)).segment((51,37)).segment((-51,37)).segment((-51,11)).close().assemble().finalize().extrude(45).union(w0.sketch().circle(66).circle(65,mode='s').finalize().extrude(155)).union(w1.sketch().arc((-66,3),(14,-64),(58,30)).arc((54,30),(54,34)).arc((-13,64),(-65,10)).arc((-63,6),(-66,3)).assemble().finalize().extrude(162))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00819353.step')
