import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.00303075181079456, -0.00011441683131856121], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.04305725049136899).extrude(1.0)
