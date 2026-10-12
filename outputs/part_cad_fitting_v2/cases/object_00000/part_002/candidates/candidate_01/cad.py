import cadquery as cq
plane = cq.Plane(origin=[-0.002805240158288628, 0.02750305181315971, -0.0038279571445662243], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).box(0.6032370328903198, 1.0, 0.6621105670928955)
