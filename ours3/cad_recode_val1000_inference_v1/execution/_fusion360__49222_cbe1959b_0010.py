import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-9,-18),(-1,-22)).segment((9,2)).segment((4,15)).segment((4,16)).segment((-9,25)).close().assemble().finalize().extrude(33).union(w0.sketch().arc((7,-8),(8,-4),(8,0)).close().assemble().finalize().extrude(196)).union(w1.sketch().arc((-8,-25),(8,0),(-8,25)).close().assemble().finalize().extrude(-78))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__49222_cbe1959b_0010.step')
