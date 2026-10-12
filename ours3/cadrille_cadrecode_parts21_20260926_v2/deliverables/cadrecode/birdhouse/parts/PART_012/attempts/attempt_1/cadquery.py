import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-91))
w1=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.sketch().segment((-100,-10),(-99,-17)).segment((-83,-16)).segment((-83,-15)).segment((83,-15)).segment((83,-16)).segment((100,-14)).segment((99,-8)).segment((66,-8)).arc((55,-10),(44,-8)).segment((43,-8)).segment((43,-7)).arc((41,-10),(39,-14)).segment((-83,-14)).segment((-83,-8)).close().assemble().finalize().extrude(182).union(w1.workplane(offset=32/2).moveTo(-68,-86).cylinder(32,15))