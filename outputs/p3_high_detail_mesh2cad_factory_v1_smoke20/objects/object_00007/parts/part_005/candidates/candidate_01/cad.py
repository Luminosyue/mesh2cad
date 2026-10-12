import cadquery as cq
plane = cq.Plane(origin=[-0.12818586826324463, -0.0005281071556254846, 0.0016543027522131462], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4027092710414404).extrude(0.25637173652648926)
