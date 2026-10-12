import cadquery as cq
plane=cq.Plane(origin=[0.,0.,0.],xDir=[1.,0.,0.],normal=[0.,0.,1.])
result=cq.Workplane(plane).moveTo(-1.5460712374090488e-13,-1.0806521811714428e-13).ellipse(1.999050307849671,0.9994905243771831,rotation_angle=-180.00000000004272).extrude(0.8)
