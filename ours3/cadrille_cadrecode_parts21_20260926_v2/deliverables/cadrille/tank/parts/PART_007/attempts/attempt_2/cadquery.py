import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.workplane(offset=8/2).cylinder(8,65).union(w0.sketch().segment((-58,62),(-55,26)).arc((-1,-65),(52,27)).segment((59,27)).segment((59,64)).segment((53,63)).arc((52,48),(50,34)).arc((-1,-57),(-43,38)).arc((-46,47),(-47,57)).arc((-52,60),(-58,62)).assemble().finalize().extrude(198))