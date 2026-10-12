import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-30))
w1=cq.Workplane('XY',origin=(0,0,-27))
r=w0.sketch().arc((-40,76),(-1,-99),(40,75)).arc((0,100),(-40,76)).assemble().finalize().extrude(55).union(w1.sketch().arc((-55,60),(26,-66),(12,83)).arc((-25,83),(-55,60)).assemble().finalize().extrude(56))