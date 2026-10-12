import cadquery as cq
w0=cq.Workplane('YZ',origin=(-98,0,0))
r=w0.sketch().segment((-100,-82),(-92,-98)).segment((-86,-94)).segment((-93,-81)).close().assemble().finalize().extrude(18).union(w0.sketch().segment((-100,-82),(-92,-99)).segment((-89,-97)).segment((-93,-91)).close().assemble().finalize().extrude(198))