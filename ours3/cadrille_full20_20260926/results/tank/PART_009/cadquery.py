import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('YZ',origin=(38,0,0))
r=w0.sketch().arc((-99,-17),(99,0),(-99,17)).arc((-90,1),(-99,-17)).assemble().push([(1,-1)]).circle(87,mode='s').finalize().extrude(119).union(w1.sketch().push([(-11,-48)]).circle(49).push([(-29,-1)]).circle(3,mode='s').finalize().extrude(-104))