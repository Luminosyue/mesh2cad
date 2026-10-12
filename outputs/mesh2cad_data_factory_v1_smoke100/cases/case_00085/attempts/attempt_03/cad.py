import cadquery as cq
plane = cq.Plane(origin=[-0.2804482877254486, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.35096170753240585).extrude(0.5608965754508972)
