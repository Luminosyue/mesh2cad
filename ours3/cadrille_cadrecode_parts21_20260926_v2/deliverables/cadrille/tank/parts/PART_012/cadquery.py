import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
w1=cq.Workplane('YZ',origin=(20,0,0))
r=w0.sketch().segment((-78,-15),(-70,-34)).segment((-13,-10)).segment((-13,18)).close().assemble().finalize().extrude(-83).union(w0.sketch().segment((-64,-38),(-55,-46)).segment((78,24)).segment((69,43)).close().assemble().finalize().extrude(75)).union(w0.sketch().segment((-75,-14),(-64,-34)).segment((-4,0)).segment((-15,20)).close().assemble().finalize().extrude(117)).union(w1.workplane(offset=-58/2).moveTo(18,0).cylinder(58,21))