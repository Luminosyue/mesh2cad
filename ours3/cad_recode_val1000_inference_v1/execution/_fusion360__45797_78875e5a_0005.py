import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-97))
r=w0.sketch().arc((-10,-9),(-9,-8),(-8,-9)).arc((9,8),(-10,-6)).close().assemble().circle(11,mode='s').finalize().extrude(193).union(w0.sketch().segment((-10,9),(3,11)).arc((-4,12),(-10,9)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-9,-10),(13,0),(-9,10)).close().assemble().finalize().extrude(71))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__45797_78875e5a_0005.step')
