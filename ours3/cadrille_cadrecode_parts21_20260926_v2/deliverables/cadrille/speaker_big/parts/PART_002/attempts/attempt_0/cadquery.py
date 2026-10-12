import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
r=w0.sketch().segment((-100,39),(-99,-41)).segment((100,-40)).segment((99,41)).close().assemble().finalize().extrude(-13)