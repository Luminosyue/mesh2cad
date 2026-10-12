import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().rect(86,132).rect(74,132,mode='s').finalize().extrude(199).union(w0.workplane(offset=199/2).box(64,134,199))