import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-59))
w1=cq.Workplane('XY',origin=(0,0,-58))
r=w0.sketch().circle(98).circle(96,mode='s').finalize().extrude(100).union(w0.sketch().arc((-18,-15),(16,15),(-1,-24)).arc((11,22),(-18,-15)).assemble().finalize().extrude(118)).union(w1.sketch().circle(97).circle(87,mode='s').finalize().extrude(99))