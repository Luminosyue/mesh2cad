import cadquery as cq
w0=cq.Workplane('YZ',origin=(-38,0,0))
w1=cq.Workplane('YZ',origin=(-41,0,0))
r=w0.sketch().segment((-28,-92),(-28,-8)).segment((55,-8)).segment((55,-84)).arc((-10,99),(-28,-92)).assemble().finalize().extrude(68).union(w0.sketch().segment((-73,50),(-73,53)).arc((-10,-99),(52,53)).segment((52,50)).segment((29,50)).arc((-10,-20),(-49,50)).close().assemble().finalize().extrude(78)).union(w1.sketch().push([(-10,0)]).circle(70).circle(12,mode='s').finalize().extrude(82))