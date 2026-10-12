import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().arc((-10,-21),(10,0),(-10,22)).close().assemble().finalize().extrude(-72).union(w0.sketch().arc((-10,-22),(10,0),(-10,22)).close().assemble().finalize().extrude(128))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00105351.step')
