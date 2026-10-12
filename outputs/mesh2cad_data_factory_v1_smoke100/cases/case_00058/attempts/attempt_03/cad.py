import cadquery as cq
plane = cq.Plane(origin=[-0.015931151807308197, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.35383810847997665).extrude(0.031862303614616394)
