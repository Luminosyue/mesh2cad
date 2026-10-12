import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('YZ',origin=(-43,0,0))
r=w0.sketch().arc((-56,-5),(-49,-4),(-43,-5)).arc((-44,2),(-43,8)).arc((-48,13),(-54,15)).arc((-63,6),(-56,-5)).assemble().finalize().extrude(50).union(w0.workplane(offset=200/2).moveTo(-53,5).cylinder(200,10)).union(w1.workplane(offset=107/2).moveTo(-5,-90).cylinder(107,10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00937785.step')
