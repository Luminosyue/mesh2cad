import cadquery as cq
w0=cq.Workplane('YZ',origin=(-98,0,0))
w1=cq.Workplane('YZ',origin=(-44,0,0))
r=w0.sketch().segment((-67,-99),(99,-99)).segment((99,-54)).segment((13,-54)).arc((-8,-52),(-29,-54)).segment((-67,-54)).close().assemble().finalize().extrude(5).union(w0.sketch().segment((-100,-60),(-99,-94)).segment((100,-94)).segment((99,-53)).close().assemble().finalize().extrude(52)).union(w1.sketch().arc((-96,-54),(-68,-100),(-30,-62)).arc((-65,-65),(-96,-54)).assemble().finalize().extrude(-41))