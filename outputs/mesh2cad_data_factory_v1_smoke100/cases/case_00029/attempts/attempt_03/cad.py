import cadquery as cq
plane = cq.Plane(origin=[-0.03606661781668663, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.44242575764656067).extrude(0.07213323563337326)
