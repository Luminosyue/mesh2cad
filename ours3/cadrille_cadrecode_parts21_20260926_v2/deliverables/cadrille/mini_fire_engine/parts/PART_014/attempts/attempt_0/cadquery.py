import cadquery as cq
w0=cq.Workplane('YZ',origin=(-26,0,0))
w1=cq.Workplane('YZ',origin=(-28,0,0))
r=w0.sketch().segment((-100,-18),(-83,-20)).segment((-83,-24)).segment((-57,-23)).segment((-42,-24)).segment((-42,-23)).segment((88,-23)).segment((88,23)).segment((-42,23)).segment((-42,24)).segment((-68,24)).segment((-83,24)).segment((-83,22)).segment((-99,22)).close().assemble().finalize().extrude(54).union(w1.workplane(offset=54/2).moveTo(67,0).cylinder(54,33))