import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-91,0))
w1=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.workplane(offset=-8/2).moveTo(0,10).cylinder(8,54).union(w0.sketch().arc((-57,23),(-11,-65),(61,10)).segment((62,10)).segment((59,64)).segment((50,63)).arc((52,39),(50,15)).arc((54,10),(50,5)).arc((-14,-56),(-43,26)).arc((-46,44),(-45,62)).segment((-56,62)).close().assemble().finalize().extrude(190)).union(w1.workplane(offset=7/2).moveTo(0,10).cylinder(7,55))