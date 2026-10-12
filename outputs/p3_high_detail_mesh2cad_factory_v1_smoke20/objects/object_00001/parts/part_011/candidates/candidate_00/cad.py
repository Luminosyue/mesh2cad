import cadquery as cq
plane = cq.Plane(origin=[-0.08907231244517877, 0.18157488454454457, -0.09510517865419388], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5692210603590209).extrude(0.19021035730838776)
