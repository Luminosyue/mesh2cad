import cadquery as cq
w0=cq.Workplane('YZ',origin=(99,0,0))
w1=cq.Workplane('XY',origin=(0,0,48))
r=w0.workplane(offset=-198/2).moveTo(32,31).cylinder(198,34).union(w0.sketch().arc((-83,-65),(-41,-65),(0,-60)).segment((84,-60)).segment((84,42)).segment((10,42)).arc((-53,23),(-83,-35)).close().assemble().finalize().extrude(-197)).union(w0.workplane(offset=-101/2).moveTo(32,31).cylinder(101,53)).union(w1.sketch().arc((-100,-20),(-64,-84),(10,-75)).arc((99,-55),(28,2)).arc((-28,54),(-100,16)).arc((-81,-2),(-100,-20)).assemble().finalize().extrude(-113))