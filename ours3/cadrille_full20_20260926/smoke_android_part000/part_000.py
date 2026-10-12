import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('YZ',origin=(33,0,0))
r=w0.sketch().segment((-18,97),(-18,98)).arc((-10,-98),(32,94)).segment((32,93)).segment((29,93)).segment((29,97)).arc((7,99),(-14,98)).segment((-14,97)).close().assemble().finalize().extrude(3).union(w0.sketch().segment((49,19),(57,16)).segment((58,19)).close().assemble().finalize().extrude(106)).union(w1.sketch().arc((-21,-7),(-20,-7),(-19,-8)).arc((-26,4),(-21,-7)).assemble().finalize().extrude(-98))