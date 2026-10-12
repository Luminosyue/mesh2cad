import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.002275342865102577, 0.0026786199632273327], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.054555282344959696).extrude(1.0)
