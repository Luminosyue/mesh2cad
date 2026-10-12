import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,87,0))
r=w0.sketch().segment((-14,-4),(5,-4)).segment((6,-2)).segment((-12,-1)).segment((-11,5)).segment((-14,5)).arc((-13,1),(-14,-4)).assemble().finalize().extrude(-187).union(w0.workplane(offset=13/2).moveTo(0,-2).cylinder(13,4))