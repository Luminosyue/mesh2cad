import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-22))
w1=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-100,-35),(6,-35)).segment((6,18)).segment((-100,18)).segment((-100,-23)).segment((-99,-23)).segment((-99,-25)).segment((-100,-25)).close().assemble().finalize().extrude(44).union(w0.workplane(offset=44/2).moveTo(-47,-8.5).box(86,53,44)).union(w1.sketch().arc((59,3),(79,12),(100,11)).arc((75,22),(59,3)).assemble().finalize().extrude(12))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0001_00010109.step')
