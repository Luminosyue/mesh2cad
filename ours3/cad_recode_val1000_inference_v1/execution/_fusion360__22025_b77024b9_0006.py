import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().arc((-6,6),(5,-7),(-4,8)).arc((-4,6),(-6,6)).assemble().finalize().extrude(200)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__22025_b77024b9_0006.step')
