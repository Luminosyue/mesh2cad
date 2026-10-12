import cadquery as cq
plane = cq.Plane(origin=[-0.0006808588701231005, -0.5, -0.0003044815768109246], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.037573763770734646).extrude(1.0)
