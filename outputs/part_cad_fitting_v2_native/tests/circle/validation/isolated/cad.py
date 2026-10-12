import cadquery as cq
plane=cq.Plane(origin=[0.,0.,0.],xDir=[1.,0.,0.],normal=[0.,0.,1.])
result=cq.Workplane(plane).moveTo(4.536849845880841e-13,1.1125266154285093e-14).circle(0.9996145181179261).extrude(0.8)
