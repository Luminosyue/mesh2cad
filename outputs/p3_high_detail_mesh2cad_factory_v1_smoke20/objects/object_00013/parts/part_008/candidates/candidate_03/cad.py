import cadquery as cq
plane = cq.Plane(origin=[-6.794736848418637e-05, -0.5, 0.06398977571419712], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.22213235006952017).extrude(1.0)
