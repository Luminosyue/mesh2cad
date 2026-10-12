import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().arc((-38,-5),(-28,-10),(-17,-10)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-25,4),(37,1)).segment((38,2)).segment((15,10)).arc((1,8),(-13,7)).close().assemble().finalize().extrude(-199))