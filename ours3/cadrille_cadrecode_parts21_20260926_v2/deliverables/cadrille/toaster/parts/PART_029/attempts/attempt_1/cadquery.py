import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,44,0))
w1=cq.Workplane('YZ',origin=(3,0,0))
r=w0.workplane(offset=-122/2).moveTo(-2,-2).cylinder(122,4).union(w0.sketch().segment((-18,7),(-17,0)).segment((-13,1)).arc((1,-6),(13,3)).segment((21,4)).segment((21,7)).segment((13,7)).arc((0,14),(-13,6)).close().assemble().finalize().extrude(53)).union(w1.sketch().arc((-100,8),(-98,7),(-97,5)).arc((-70,-16),(-35,-18)).arc((-35,-15),(-32,-16)).arc((-25,17),(-58,21)).arc((-78,18),(-95,8)).close().assemble().finalize().extrude(4))