import cadquery as cq
w0=cq.Workplane('YZ',origin=(17,0,0))
w1=cq.Workplane('YZ',origin=(-10,0,0))
r=w0.sketch().segment((-99,-66),(-57,-87)).segment((-57,-88)).segment((-55,-88)).segment((-22,-100)).segment((-17,-85)).segment((-24,-83)).arc((-62,-29),(-99,-66)).assemble().finalize().extrude(-117).union(w0.sketch().segment((-83,-76),(-24,-99)).segment((-11,-64)).segment((-70,-41)).close().assemble().finalize().extrude(82)).union(w1.workplane(offset=-69/2).moveTo(-53,-52).cylinder(69,37))