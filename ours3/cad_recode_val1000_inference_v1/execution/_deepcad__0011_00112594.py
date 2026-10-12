import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(77,0,0))
r=w0.sketch().arc((-95,33),(-89,-44),(-24,-97)).segment((-24,-98)).segment((-21,-98)).arc((0,-100),(21,-98)).segment((24,-98)).segment((24,-97)).arc((38,-92),(50,-86)).segment((33,-86)).segment((33,-70)).arc((30,-69),(33,-68)).segment((33,-63)).segment((72,-63)).segment((72,-69)).arc((83,-56),(91,-41)).segment((89,-41)).segment((89,-38)).segment((92,-38)).arc((99,-14),(100,11)).arc((81,6),(67,19)).segment((67,25)).segment((64,25)).arc((65,27),(65,29)).segment((65,33)).segment((63,33)).arc((0,91),(-63,33)).close().assemble().finalize().extrude(-154).union(w0.sketch().arc((-81,-59),(-11,-68),(50,-87)).arc((11,99),(-81,-59)).assemble().finalize().extrude(-137))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0011_00112594.step')
