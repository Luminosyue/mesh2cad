import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,27))
w1=cq.Workplane('YZ',origin=(35,0,0))
r=w0.sketch().segment((-42,95),(-38,-99)).segment((34,-97)).segment((33,-47)).arc((39,-20),(32,7)).segment((31,97)).close().assemble().finalize().extrude(-124).union(w0.workplane(offset=-91/2).moveTo(0,34).cylinder(91,61)).union(w1.sketch().arc((-58,-76),(-11,-71),(26,-97)).arc((20,94),(-58,-76)).assemble().finalize().extrude(-72))