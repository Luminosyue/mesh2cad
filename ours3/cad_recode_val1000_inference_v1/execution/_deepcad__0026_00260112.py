import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,93))
r=w0.sketch().segment((-23,6),(-21,13)).arc((-22,-19),(11,-27)).segment((10,-27)).segment((10,-25)).segment((12,-25)).segment((12,-27)).arc((26,13),(-17,20)).segment((-13,19)).segment((-15,11)).arc((-13,-10),(-23,6)).assemble().finalize().extrude(-160).union(w0.workplane(offset=-57/2).moveTo(0,0).cylinder(57,23)).union(w0.workplane(offset=-34/2).moveTo(0,0).cylinder(34,23)).union(w1.sketch().arc((-23,6),(1,-27),(29,3)).arc((27,4),(29,5)).arc((10,26),(-17,18)).arc((-17,10),(-23,6)).assemble().finalize().extrude(-193))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00260112.step')
