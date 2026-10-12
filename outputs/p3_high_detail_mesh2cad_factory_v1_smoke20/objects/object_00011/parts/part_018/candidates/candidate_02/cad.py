import cadquery as cq
plane = cq.Plane(origin=[0.0008053440950999552, 0.23420408814365745, -0.06761074811220169], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3888615350070535).extrude(0.13522149622440338)
