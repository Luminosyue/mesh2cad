import cadquery as cq
plane = cq.Plane(origin=[-0.0778670608997345, 0.00703174407873796, -0.040943050720305], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.28960528856336354).extrude(0.155734121799469)
