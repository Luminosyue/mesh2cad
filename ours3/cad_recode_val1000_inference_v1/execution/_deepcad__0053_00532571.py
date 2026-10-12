import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(97,0,0))
r=w0.sketch().segment((-7,-13),(6,-13)).arc((-6,0),(6,11)).segment((-7,11)).close().assemble().finalize().extrude(-193).union(w0.sketch().segment((-7,13),(7,10)).arc((0,13),(-7,13)).assemble().finalize().extrude(-70)).union(w1.sketch().segment((-5,-10),(7,-10)).arc((0,-8),(-5,-5)).close().assemble().finalize().extrude(-197))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00532571.step')
