import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-45))
w1=cq.Workplane('ZX',origin=(0,-45,0))
r=w0.sketch().circle(99).circle(93,mode='s').finalize().extrude(-54).union(w0.sketch().segment((-70,-39),(-49,-51)).segment((70,39)).segment((49,59)).close().assemble().finalize().extrude(-36)).union(w1.sketch().push([(-69,0)]).circle(14).push([(-68.5,0)]).rect(13,24,mode='s').finalize().extrude(104))