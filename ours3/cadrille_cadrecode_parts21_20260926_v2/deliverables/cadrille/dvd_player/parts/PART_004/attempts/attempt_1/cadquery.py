import cadquery as cq
w0=cq.Workplane('YZ',origin=(77,0,0))
w1=cq.Workplane('XY',origin=(0,0,84))
r=w0.sketch().segment((-21,-96),(18,-100)).segment((22,-67)).arc((1,-92),(-21,-67)).close().assemble().reset().face(w0.sketch().arc((-21,-60),(1,-35),(23,-60)).segment((23,-27)).segment((15,-27)).segment((15,67)).segment((21,67)).segment((21,87)).arc((1,100),(-20,84)).segment((15,84)).segment((15,-27)).segment((-18,-27)).close().assemble()).finalize().extrude(-154).union(w1.workplane(offset=-147/2).moveTo(74.5,0).box(5,42,147))