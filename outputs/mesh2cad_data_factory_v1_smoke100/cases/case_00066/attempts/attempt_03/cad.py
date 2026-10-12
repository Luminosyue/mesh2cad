import cadquery as cq
plane = cq.Plane(origin=[-0.011268779635429382, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.37729544937610626).extrude(0.022537559270858765)
