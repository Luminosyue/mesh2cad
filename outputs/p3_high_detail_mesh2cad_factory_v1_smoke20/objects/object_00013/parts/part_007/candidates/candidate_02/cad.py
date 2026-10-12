import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.10675047810262589, 0.013505607954163437], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.16287891686722208).extrude(1.0)
