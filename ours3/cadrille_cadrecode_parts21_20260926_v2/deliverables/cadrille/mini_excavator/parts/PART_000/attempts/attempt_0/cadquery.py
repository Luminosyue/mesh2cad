import cadquery as cq
w0=cq.Workplane('YZ',origin=(51,0,0))
w1=cq.Workplane('YZ',origin=(53,0,0))
r=w0.sketch().segment((-62,-66),(27,-100)).segment((31,-90)).arc((93,-24),(69,62)).segment((73,72)).segment((-16,100)).segment((-20,90)).arc((-93,24),(-60,-62)).close().assemble().finalize().extrude(-98).union(w1.sketch().arc((-99,11),(89,-36),(-93,36)).arc((-97,24),(-99,11)).assemble().finalize().extrude(-92))