import cadquery as cq
w0=cq.Workplane('YZ',origin=(-82,0,0))
w1=cq.Workplane('XY',origin=(0,0,10))
r=w0.sketch().segment((-100,-65),(89,-69)).segment((92,13)).segment((100,13)).segment((100,15)).segment((92,15)).segment((92,17)).segment((-99,69)).close().assemble().finalize().extrude(162).union(w1.sketch().push([(0,-6.5)]).rect(162,187).push([(0,-7)]).rect(154,172,mode='s').finalize().extrude(-79))