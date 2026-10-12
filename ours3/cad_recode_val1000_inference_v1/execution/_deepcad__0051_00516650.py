import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-33))
r=w0.sketch().segment((-34,33),(-33,33)).segment((-33,29)).segment((-27,29)).segment((-27,18)).segment((-18,18)).arc((1,-41),(61,-45)).segment((61,-47)).segment((100,-53)).segment((100,-49)).segment((61,-43)).segment((61,-45)).arc((45,-27),(65,-10)).segment((65,-9)).segment((94,-14)).arc((97,18),(76,44)).segment((96,44)).segment((96,60)).segment((86,60)).segment((86,66)).segment((39,66)).segment((39,60)).segment((38,60)).segment((38,44)).segment((47,44)).arc((26,36),(11,20)).arc((1,-14),(-1,21)).arc((-13,39),(2,55)).arc((1,60),(2,66)).segment((-18,66)).segment((-18,60)).segment((-27,60)).segment((-27,65)).segment((-34,65)).close().assemble().finalize().extrude(16).union(w0.sketch().segment((-100,-66),(-10,-66)).segment((-10,-49)).segment((-78,-49)).segment((-78,-50)).segment((-80,-50)).segment((-80,-49)).segment((-100,-49)).close().assemble().push([(-24,49)]).rect(114,16).finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0051_00516650.step')
