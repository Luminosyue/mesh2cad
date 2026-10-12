import cadquery as cq
plane = cq.Plane(origin=[-0.001516116475888174, -0.6621103278147878, -0.20918141305446625], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.7183413327422753).extrude(0.4183628261089325)
