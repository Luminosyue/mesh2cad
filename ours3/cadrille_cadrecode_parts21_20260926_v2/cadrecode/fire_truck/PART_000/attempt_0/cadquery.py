import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-30,0))
w1=cq.Workplane('XY',origin=(0,0,-64))
r=w0.workplane(offset=-60/2).moveTo(-19,0).cylinder(60,56).union(w0.sketch().arc((-79,15),(-41,-93),(61,-50)).arc((21,90),(-79,15)).assemble().finalize().extrude(77)).union(w0.workplane(offset=127/2).moveTo(-19,0).cylinder(127,60)).union(w1.sketch().arc((-96,10),(89,-41),(-89,34)).arc((-94,23),(-96,10)).assemble().finalize().extrude(91))