import cadquery as cq
plane = cq.Plane(origin=[-0.44779253005981445, 0.0017685291469039244, 0.012848026907778086], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.43157879076552647).extrude(0.8955850601196289)
