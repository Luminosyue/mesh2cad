import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('YZ',origin=(-92,0,0))
r=w0.sketch().arc((-8,12),(7,-13),(-4,14)).arc((-5,12),(-8,12)).assemble().finalize().extrude(200).union(w1.sketch().arc((-11,10),(10,-11),(-8,13)).arc((-9,11),(-11,10)).assemble().finalize().extrude(125))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0095_00954360.step')
