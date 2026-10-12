import cadquery as cq
plane = cq.Plane(origin=[-0.44309720396995544, 0.022124854594877397, -0.027818394587132693], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4413070379976895).extrude(0.8861944079399109)
