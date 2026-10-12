import cadquery as cq
w0=cq.Workplane('YZ',origin=(77,0,0))
r=w0.sketch().segment((-21,-99),(18,-100)).segment((21,93)).segment((-19,94)).arc((-15,89),(-11,84)).segment((15,84)).segment((15,-92)).segment((-7,-92)).segment((-7,-89)).arc((-14,-94),(-21,-90)).close().assemble().finalize().extrude(-154).union(w0.workplane(offset=-149/2).moveTo(16,-12).box(2,134,149))