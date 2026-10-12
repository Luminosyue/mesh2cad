import cadquery as cq
w0=cq.Workplane('YZ',origin=(-96,0,0))
r=w0.sketch().segment((-56,-93),(-55,-100)).segment((59,3)).segment((44,20)).segment((43,16)).segment((36,18)).segment((37,23)).segment((-56,100)).segment((1,53)).arc((28,28),(48,-4)).close().assemble().finalize().extrude(194)