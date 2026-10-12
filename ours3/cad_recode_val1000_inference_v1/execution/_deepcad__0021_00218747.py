import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-97,0))
r=w0.sketch().segment((6,-2),(6,2)).arc((-6,-1),(6,-2)).assemble().finalize().extrude(200).union(w1.sketch().arc((-6,-2),(0,-5),(6,-2)).close().assemble().finalize().extrude(111))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0021_00218747.step')
