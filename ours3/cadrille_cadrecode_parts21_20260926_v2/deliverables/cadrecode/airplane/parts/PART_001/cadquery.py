import cadquery as cq
w0=cq.Workplane('YZ',origin=(96,0,0))
w1=cq.Workplane('YZ',origin=(59,0,0))
r=w0.sketch().segment((-56,13),(61,-14)).arc((2,14),(-56,13)).assemble().finalize().extrude(-123).union(w0.sketch().segment((-61,13),(-59,12)).segment((-59,14)).close().assemble().finalize().extrude(4)).union(w1.sketch().segment((-15,11),(53,-7)).segment((56,-3)).segment((-15,20)).close().assemble().finalize().extrude(-159))