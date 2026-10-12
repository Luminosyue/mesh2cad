import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-64))
w1=cq.Workplane('XY',origin=(0,0,-43))
r=w0.sketch().arc((-76,-63),(-44,-77),(-10,-82)).close().assemble().reset().face(w0.sketch().segment((-83,53),(-63,23)).arc((-61,-15),(-42,-48)).segment((-42,-63)).arc((-33,-67),(-24,-71)).segment((-2,-100)).arc((19,-96),(39,-89)).segment((10,-60)).arc((40,-49),(60,-25)).segment((89,-44)).arc((96,-21),(99,2)).segment((100,2)).segment((99,3)).arc((96,21),(89,38)).segment((89,43)).segment((88,43)).arc((86,49),(83,53)).segment((39,92)).arc((18,96),(-3,99)).segment((-36,93)).arc((-57,80),(-76,64)).close().assemble()).finalize().extrude(128).union(w1.sketch().arc((-93,-37),(-91,-36),(-89,-36)).arc((-1,63),(41,-59)).arc((47,-74),(46,-90)).arc((98,-10),(69,73)).arc((49,39),(62,1)).arc((-45,45),(-93,-37)).assemble().finalize().extrude(97))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00787070.step')
