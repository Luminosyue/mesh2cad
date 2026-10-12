import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-78))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-63,-49),(-63,-45)).arc((-79,0),(-63,45)).segment((-63,49)).arc((-80,0),(-63,-49)).assemble().reset().face(w0.sketch().arc((-59,-54),(0,-80),(59,-54)).segment((56,-54)).arc((0,-80),(-56,-54)).close().assemble()).reset().face(w0.sketch().segment((-59,54),(-56,54)).arc((0,80),(56,54)).segment((59,54)).arc((0,80),(-59,54)).assemble()).reset().face(w0.sketch().arc((63,-49),(80,0),(63,49)).segment((63,45)).arc((79,0),(63,-45)).close().assemble()).finalize().extrude(178).union(w1.sketch().arc((-70,39),(-79,-11),(-58,-55)).arc((-30,-54),(-8,-74)).arc((39,-60),(74,-30)).arc((34,-1),(79,5)).arc((19,77),(-68,42)).arc((-66,39),(-70,39)).assemble().finalize().extrude(145))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00504143.step')
