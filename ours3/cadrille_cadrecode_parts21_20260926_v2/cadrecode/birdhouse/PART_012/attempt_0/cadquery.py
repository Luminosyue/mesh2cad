import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-91))
w1=cq.Workplane('YZ',origin=(-83,0,0))
r=w0.sketch().segment((-100,-9),(-99,-17)).segment((100,-14)).segment((99,-8)).segment((88,-8)).segment((88,-15)).segment((-80,-15)).segment((-80,-8)).close().assemble().finalize().extrude(182).union(w1.workplane(offset=-7/2).moveTo(0,-69).cylinder(7,17))