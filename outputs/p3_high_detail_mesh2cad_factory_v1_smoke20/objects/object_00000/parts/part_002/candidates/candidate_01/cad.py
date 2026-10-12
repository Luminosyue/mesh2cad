import cadquery as cq
plane = cq.Plane(origin=[-0.005463138908650578, 0.023222475963527583, -0.3016185164451599], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.44343498785304264).extrude(0.6032370328903198)
