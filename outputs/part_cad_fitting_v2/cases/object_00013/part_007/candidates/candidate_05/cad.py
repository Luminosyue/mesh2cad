import cadquery as cq
plane = cq.Plane(origin=[0.05357670446918872, 52.123962185056484, -0.21704843640327454], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(52.118245711335376).workplane(offset=0.4340968728065491).circle(52.13254011681754).loft(ruled=True)
