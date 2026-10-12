import cadquery as cq
plane = cq.Plane(origin=[0.0074611718623505685, -0.69853806499151, -0.08307639509439468], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.7496048844238449).extrude(0.16615279018878937)
