import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,18,0))
r=w0.sketch().segment((-95,30),(-94,19)).arc((-99,-5),(-92,-28)).segment((-91,-17)).segment((-66,-24)).arc((-69,13),(-48,44)).segment((-48,52)).segment((-41,52)).arc((0,71),(41,52)).segment((53,52)).segment((53,44)).arc((71,2),(53,-40)).segment((53,-48)).segment((47,-48)).arc((0,-71),(-47,-52)).segment((-53,-52)).segment((-53,-44)).arc((-61,-35),(-67,-23)).segment((-70,-23)).segment((-71,39)).arc((-76,33),(-79,26)).close().assemble().reset().face(w0.sketch().segment((-79,-59),(-43,-90)).segment((-43,-89)).arc((51,-84),(98,2)).segment((99,2)).segment((98,13)).segment((97,13)).arc((92,39),(75,61)).segment((74,71)).segment((65,70)).arc((41,89),(11,97)).segment((0,100)).segment((-1,99)).arc((-54,82),(-76,31)).arc((-100,-3),(-83,-42)).arc((-81,-48),(-78,-54)).close().assemble()).finalize().extrude(-36)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00987041.step')
