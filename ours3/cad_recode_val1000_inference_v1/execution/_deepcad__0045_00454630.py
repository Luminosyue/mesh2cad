import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-82,0))
w1=cq.Workplane('YZ',origin=(21,0,0))
r=w0.workplane(offset=-18/2).moveTo(-1,0).cylinder(18,8).union(w0.workplane(offset=4/2).moveTo(0,-7).cylinder(4,14)).union(w0.workplane(offset=82/2).moveTo(0,-7).cylinder(82,14)).union(w1.sketch().arc((82,-4),(91,-6),(100,-7)).arc((96,0),(95,7)).arc((90,6),(86,0)).segment((82,0)).close().assemble().finalize().extrude(-15))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00454630.step')
