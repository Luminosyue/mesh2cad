import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.sketch().arc((13,-3),(15,0),(13,3)).close().assemble().finalize().extrude(16).union(w0.sketch().arc((8,-64),(-11,25),(64,-15)).arc((-41,49),(8,-64)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-41,49),(11,59),(56,29)).arc((11,63),(-41,49)).assemble().finalize().extrude(149))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00650807.step')
