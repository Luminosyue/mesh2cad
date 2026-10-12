import cadquery as cq
w0=cq.Workplane('YZ',origin=(-75,0,0))
w1=cq.Workplane('YZ',origin=(-60,0,0))
r=w0.sketch().segment((-100,-65),(42,-65)).segment((42,-43)).segment((100,5)).segment((69,45)).segment((42,25)).segment((42,65)).segment((-100,65)).close().assemble().push([(-32.5,-3.5)]).rect(113,109,mode='s').finalize().extrude(150).union(w1.sketch().push([(-14,0)]).circle(66).push([(-14.5,0)]).rect(111,72,mode='s').finalize().extrude(-4))