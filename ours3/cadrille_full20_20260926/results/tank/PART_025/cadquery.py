import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-85,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-94,17),(-69,-92),(23,-41)).arc((-49,-61),(-94,17)).assemble().finalize().extrude(-36).union(w0.sketch().segment((-84,-70),(-57,-98)).segment((3,-40)).segment((-11,-26)).segment((-11,-18)).segment((-19,-18)).segment((-19,-21)).close().assemble().finalize().extrude(48)).union(w1.sketch().push([(-39,50)]).circle(21).circle(19,mode='s').finalize().extrude(30))