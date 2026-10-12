import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0203181382503783, -0.13216691038628933], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.22590716011454287).extrude(1.0)
