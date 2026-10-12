import cadquery as cq
plane = cq.Plane(origin=[-0.09460671246051788, 0.01323046067022975, -0.013471761087841108], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.366021678141213).extrude(0.18921342492103577)
