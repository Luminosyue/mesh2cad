import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-78))
w1=cq.Workplane('ZX',origin=(0,79,0))
r=w0.sketch().push([(-38,27)]).circle(51).circle(29,mode='s').finalize().extrude(-19).union(w0.sketch().segment((-99,-94),(28,-99)).segment((32,11)).segment((18,11)).arc((-38,100),(-94,12)).close().assemble().reset().face(w0.sketch().segment((-90,-84),(-58,-92)).segment((-40,1)).segment((-72,8)).close().assemble(),mode='s').push([(-38,27)]).circle(27,mode='s').finalize().extrude(-18)).union(w1.sketch().push([(-88,-38)]).circle(11).circle(4,mode='s').finalize().extrude(-179))