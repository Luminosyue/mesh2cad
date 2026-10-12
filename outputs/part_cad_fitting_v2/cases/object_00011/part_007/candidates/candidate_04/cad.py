import cadquery as cq
plane = cq.Plane(origin=[-0.0003100585673574423, -0.007491248214564497, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03305751216662165).extrude(1.0)
