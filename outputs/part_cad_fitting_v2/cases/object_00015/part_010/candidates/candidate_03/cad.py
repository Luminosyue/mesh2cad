import cadquery as cq
plane = cq.Plane(origin=[2122.8452633029215, -2456.0991231580847, -27.65257471888069], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(3246.4738247114533)
