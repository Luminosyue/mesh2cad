import cadquery as cq
plane = cq.Plane(origin=[-0.3268141448497772, 0.014562872709240504, 0.2300197395640592], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.44641894690562267).extrude(0.6536282896995544)
