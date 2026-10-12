import cadquery as cq
plane = cq.Plane(origin=[-0.35350415110588074, 0.03840834432494325, 0.021780683542314206], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.3813476555606213).extrude(0.7070083022117615)
