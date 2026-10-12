import cadquery as cq
plane = cq.Plane(origin=[-0.44309720396995544, 0.021374559044552904, -0.030315210029316156], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.43965138289665706).extrude(0.8861944079399109)
