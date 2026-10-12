import cadquery as cq
plane = cq.Plane(origin=[0.007714370670936886, -0.5, -0.24931179010281657], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3623313573224672).extrude(1.0)
