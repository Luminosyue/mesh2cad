import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('ZX',origin=(0,57,0))
r=w0.sketch().segment((-49,87),(7,69)).segment((12,86)).segment((-44,100)).close().assemble().finalize().extrude(50).union(w0.sketch().push([(-8,-12)]).circle(88).circle(84,mode='s').finalize().extrude(66)).union(w1.sketch().push([(-55,-19)]).circle(13).push([(-55,-19.5)]).rect(16,5,mode='s').finalize().extrude(-117))