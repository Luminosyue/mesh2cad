import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('YZ',origin=(-97,0,0))
r=w0.sketch().segment((-100,52),(-99,-98)).segment((22,-98)).segment((19,53)).close().assemble().finalize().extrude(108).union(w0.sketch().segment((-99,91),(-98,-99)).segment((21,-98)).segment((18,92)).close().assemble().finalize().extrude(198)).union(w1.sketch().segment((-99,-98),(21,-98)).segment((21,-70)).arc((22,-55),(21,-40)).segment((21,1)).segment((-99,1)).segment((-99,-40)).arc((-100,-55),(-99,-70)).close().assemble().finalize().extrude(101))