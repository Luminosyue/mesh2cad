import cadquery as cq
plane = cq.Plane(origin=[-0.17483873858262397, -0.4049079716205597, 14.767596036811044], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(14.787524467798777).extrude(0.8098159432411194)
