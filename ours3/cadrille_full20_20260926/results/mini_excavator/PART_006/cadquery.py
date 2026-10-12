import cadquery as cq
w0=cq.Workplane('YZ',origin=(-67,0,0))
w1=cq.Workplane('YZ',origin=(-63,0,0))
r=w0.sketch().segment((-31,-62),(-21,-94)).segment((-14,-92)).segment((-14,-99)).segment((0,-99)).segment((0,-87)).segment((27,-77)).segment((16,-45)).segment((9,-47)).segment((9,-40)).segment((-6,-40)).segment((-6,-52)).close().assemble().finalize().extrude(-33).union(w0.sketch().segment((-100,64),(-22,7)).segment((17,41)).segment((-8,65)).arc((-19,67),(-27,74)).segment((-86,99)).close().assemble().finalize().extrude(-28)).union(w1.workplane(offset=-30/2).moveTo(-12,36).cylinder(30,27))