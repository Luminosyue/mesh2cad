import cadquery as cq
plane = cq.Plane(origin=[-0.37156492471694946, 0.4235934532359067, 10.736422105352046], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(10.729145802337342).extrude(0.7431298494338989)
