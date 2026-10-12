import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('YZ',origin=(-3,0,0))
r=w0.sketch().segment((-2,-4),(1,-4)).arc((5,-3),(6,-1)).segment((6,1)).segment((5,1)).arc((3,3),(0,1)).segment((0,-1)).arc((-1,-1),(-2,-4)).assemble().finalize().extrude(200).union(w1.sketch().arc((-35,-8),(-33,-8),(-31,-7)).arc((-33,-6),(-35,-8)).assemble().finalize().extrude(2))