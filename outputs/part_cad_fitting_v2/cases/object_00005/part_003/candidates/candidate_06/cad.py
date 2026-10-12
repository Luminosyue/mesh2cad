import cadquery as cq
plane = cq.Plane(origin=[-3.9036433568801927, 98.39311272284836, 1.8318034078660903], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(98.49062508286279)
