import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,90))
w1=cq.Workplane('XY',origin=(0,0,93))
r=w0.workplane(offset=-184/2).cylinder(184,24).union(w0.sketch().segment((-100,55),(-54,-99)).segment((100,-55)).segment((54,99)).close().assemble().finalize().extrude(-163)).union(w1.sketch().arc((-86,10),(66,-56),(26,94)).arc((18,88),(10,88)).arc((-17,80),(-41,67)).arc((-45,67),(-49,66)).segment((-49,10)).close().assemble().finalize().extrude(-162))