import cadquery as cq
w0=cq.Workplane('YZ',origin=(-36,0,0))
w1=cq.Workplane('ZX',origin=(0,-63,0))
r=w0.sketch().segment((-100,-8),(-73,-50)).segment((100,8)).segment((73,50)).close().assemble().finalize().extrude(65).union(w0.sketch().segment((-77,-39),(-56,-47)).segment((-55,-45)).segment((-53,-46)).segment((77,39)).segment((56,47)).segment((-77,-36)).close().assemble().finalize().extrude(124)).union(w1.sketch().arc((25,-60),(-15,-85),(29,-66)).arc((23,-66),(25,-60)).assemble().finalize().extrude(98))