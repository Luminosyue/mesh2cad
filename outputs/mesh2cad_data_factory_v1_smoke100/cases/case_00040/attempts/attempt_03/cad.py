import cadquery as cq
plane = cq.Plane(origin=[-0.010606148280203342, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4406564086675644).extrude(0.021212296560406685)
