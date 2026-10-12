import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-18,0))
r=w0.sketch().segment((-33,-100),(14,-100)).segment((14,-35)).segment((-33,-35)).segment((-33,-70)).arc((-31,-71),(-33,-72)).close().assemble().push([(8,78.5)]).rect(50,43).finalize().extrude(36)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00400000.step')
