import cadquery as cq
plane = cq.Plane(origin=[-0.18342325091362, 0.004246602573914515, -0.06003147532057929], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.38258359570822137).extrude(0.36684650182724)
