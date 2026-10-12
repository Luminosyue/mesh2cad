import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().arc((-8,-97),(0,-96),(8,-97)).segment((8,-13)).segment((4,-13)).segment((4,-11)).segment((8,-11)).segment((8,87)).segment((8,100)).arc((0,99),(-8,99)).segment((-8,-11)).segment((-4,-11)).segment((-4,-13)).segment((-8,-13)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__53233_8dbca22c_0002.step')
