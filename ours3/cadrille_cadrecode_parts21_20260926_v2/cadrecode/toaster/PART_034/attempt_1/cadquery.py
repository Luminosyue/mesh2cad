import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,61))
w1=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().segment((-35,4),(-25,4)).segment((-25,0)).segment((-2,0)).segment((-2,4)).segment((6,4)).segment((6,2)).segment((29,2)).segment((29,-4)).segment((6,-4)).segment((6,-6)).segment((-5,-6)).segment((-5,-5)).segment((-7,-5)).segment((35,3)).segment((34,6)).close().assemble().finalize().extrude(-139).union(w0.sketch().push([(-26,0)]).circle(5).circle(2,mode='s').finalize().extrude(24)).union(w1.sketch().push([(70,0)]).circle(30).circle(22,mode='s').finalize().extrude(-10))