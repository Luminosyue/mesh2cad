import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-4,0))
r=w0.sketch().segment((-8,-100),(8,-100)).segment((8,100)).segment((-8,100)).segment((-8,-15)).segment((-5,-12)).segment((8,-24)).segment((8,56)).segment((-8,56)).close().assemble().finalize().extrude(8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00856966.step')
