import cadquery as cq
w0=cq.Workplane('YZ',origin=(-1,0,0))
w1=cq.Workplane('ZX',origin=(0,89,0))
r=w0.sketch().segment((-100,-13),(-12,-13)).segment((-12,12)).arc((-55,-1),(-100,-13)).assemble().reset().face(w0.sketch().arc((38,6),(55,-3),(73,-10)).segment((73,-13)).segment((83,-13)).segment((83,-10)).arc((92,-7),(100,5)).segment((98,5)).arc((90,-1),(83,3)).segment((83,6)).close().assemble()).finalize().extrude(-3).union(w1.sketch().segment((-12,-4),(-12,6)).arc((-14,1),(-12,-4)).assemble().finalize().extrude(-189))