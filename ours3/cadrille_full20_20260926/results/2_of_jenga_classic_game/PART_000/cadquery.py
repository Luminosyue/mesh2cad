import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('ZX',origin=(0,-97,0))
r=w0.sketch().segment((-100,-34),(-99,-43)).arc((-100,-57),(-97,-70)).segment((-96,-79)).segment((-93,-79)).arc((-74,-85),(-55,-77)).segment((-52,-77)).segment((-53,-68)).arc((-52,-54),(-56,-41)).segment((-57,-31)).segment((-60,-31)).arc((-79,-29),(-97,-34)).close().assemble().finalize().extrude(198).union(w1.sketch().segment((-99,-90),(-99,-34)).arc((-100,-62),(-99,-90)).assemble().finalize().extrude(166))