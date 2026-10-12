import cadquery as cq
plane = cq.Plane(origin=[-0.2334364503622055, -0.08640997767263786, 0.07799875614626725], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.40905952040292193).extrude(0.466872900724411)
