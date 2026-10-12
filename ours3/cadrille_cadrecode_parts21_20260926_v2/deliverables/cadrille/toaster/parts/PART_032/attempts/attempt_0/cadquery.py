import cadquery as cq
w0=cq.Workplane('YZ',origin=(-86,0,0))
r=w0.workplane(offset=-14/2).moveTo(4,-1).cylinder(14,8).union(w0.sketch().segment((-7,9),(-1,-9)).segment((3,-8)).segment((3,6)).segment((0,9)).close().assemble().finalize().extrude(181)).union(w0.workplane(offset=186/2).moveTo(0,0.5).box(2,17,186))