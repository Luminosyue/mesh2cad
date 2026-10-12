import cadquery as cq
plane = cq.Plane(origin=[-0.453693151473999, 0.0012646443947490482, 0.0126930451628962], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4264797709748055).extrude(0.907386302947998)
