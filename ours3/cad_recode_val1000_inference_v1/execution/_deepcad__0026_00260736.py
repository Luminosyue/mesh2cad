import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,80,0))
w1=cq.Workplane('ZX',origin=(0,52,0))
r=w0.sketch().arc((-77,62),(-99,-5),(-63,-76)).arc((-59,-78),(-56,-81)).arc((-46,-87),(-35,-92)).arc((-25,-95),(-15,-97)).arc((10,-98),(35,-93)).arc((36,-89),(39,-87)).arc((48,-85),(56,-81)).arc((57,-79),(59,-79)).arc((99,-5),(71,69)).arc((64,75),(57,80)).arc((5,99),(-47,87)).arc((-14,72),(4,41)).arc((57,-1),(38,-65)).arc((-35,-45),(-46,33)).arc((-65,46),(-77,62)).assemble().finalize().extrude(-160).union(w0.sketch().segment((-100,-8),(-55,-10)).arc((-11,56),(56,13)).segment((98,12)).arc((-4,99),(-100,-8)).assemble().finalize().extrude(-121)).union(w1.sketch().arc((-57,-10),(-52,24),(-32,48)).arc((-92,37),(-57,-10)).assemble().finalize().extrude(-93))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00260736.step')
