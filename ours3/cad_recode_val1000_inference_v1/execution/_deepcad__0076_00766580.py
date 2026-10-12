import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-47,0))
r=w0.sketch().arc((-78,-85),(-29,-92),(14,-70)).segment((14,-75)).segment((16,-75)).segment((16,-66)).arc((20,18),(-19,85)).segment((-19,100)).segment((-78,100)).segment((-78,-28)).segment((-42,-28)).arc((-43,-40),(-42,-53)).segment((-78,-53)).close().assemble().finalize().extrude(94).union(w0.sketch().segment((-78,-100),(78,-100)).segment((78,100)).segment((-78,100)).segment((-78,-28)).segment((-46,21)).segment((78,-44)).segment((78,44)).segment((73,44)).arc((56,61),(37,44)).segment((-78,44)).segment((-78,-28)).segment((-46,-28)).arc((-47,-40),(-46,-53)).segment((-78,-53)).close().assemble().finalize().extrude(94))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00766580.step')
