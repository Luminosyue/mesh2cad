import cadquery as cq
w0=cq.Workplane('YZ',origin=(49,0,0))
w1=cq.Workplane('YZ',origin=(51,0,0))
r=w0.sketch().arc((-84,16),(84,-49),(-60,66)).arc((-77,43),(-84,16)).assemble().finalize().extrude(-100).union(w0.sketch().segment((-93,-36),(-84,-36)).arc((0,-96),(84,-36)).segment((93,-36)).segment((93,36)).segment((84,36)).arc((0,96),(-84,36)).segment((-93,36)).close().assemble().finalize().extrude(-71)).union(w1.sketch().arc((-81,-46),(79,40),(-78,-51)).segment((-10,-51)).segment((-10,-28)).arc((61,26),(-25,37)).segment((-81,37)).close().assemble().finalize().extrude(-100))