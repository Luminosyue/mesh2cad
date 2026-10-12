import cadquery as cq
plane = cq.Plane(origin=[-0.3900013566017151, -0.20873879694498687, 26.228514387300855], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(26.25152467852082).extrude(0.7800027132034302)
