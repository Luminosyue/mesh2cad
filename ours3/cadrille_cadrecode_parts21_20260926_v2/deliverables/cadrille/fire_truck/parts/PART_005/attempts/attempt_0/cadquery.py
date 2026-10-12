import cadquery as cq
w0=cq.Workplane('YZ',origin=(-26,0,0))
w1=cq.Workplane('YZ',origin=(-24,0,0))
r=w0.workplane(offset=-28/2).moveTo(0,5).cylinder(28,29).union(w0.sketch().arc((-27,16),(-26,13),(-25,10)).arc((10,-26),(27,-72)).arc((84,10),(-10,35)).arc((-19,26),(-27,16)).assemble().finalize().extrude(77)).union(w0.sketch().arc((-55,73),(-78,-60),(56,-77)).segment((56,-66)).segment((70,-66)).arc((92,38),(-1,99)).arc((-31,93),(-55,73)).assemble().finalize().extrude(76)).union(w1.sketch().arc((-41,86),(26,-95),(-27,91)).segment((-27,86)).close().assemble().finalize().extrude(77))