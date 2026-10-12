import cadquery as cq
w0=cq.Workplane('YZ',origin=(-88,0,0))
w1=cq.Workplane('XY',origin=(0,0,12))
r=w0.workplane(offset=-11/2).moveTo(50,7).cylinder(11,34).union(w0.sketch().segment((-50,29),(-48,29)).arc((-47,31),(-45,29)).segment((86,-23)).segment((100,12)).segment((-43,49)).close().assemble().finalize().extrude(180)).union(w1.sketch().arc((10,22),(-83,-46),(26,-10)).arc((93,47),(10,22)).assemble().finalize().extrude(-51))