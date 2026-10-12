import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,93))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-72,8),(-65,-33),(-34,-63)).close().assemble().reset().face(w0.sketch().segment((-59,39),(11,71)).arc((-26,68),(-59,39)).assemble()).reset().face(w0.sketch().arc((-11,-71),(26,-68),(59,-39)).close().assemble()).reset().face(w0.sketch().segment((34,63),(72,-8)).arc((65,33),(34,63)).assemble()).finalize().extrude(-193).union(w0.sketch().arc((-58,-42),(-56,-38),(-54,-34)).arc((-56,-27),(-55,-20)).arc((-57,-15),(-58,-10)).close().assemble().finalize().extrude(-186)).union(w1.sketch().arc((-72,-7),(-64,-14),(-55,-21)).arc((36,47),(26,-54)).arc((27,-60),(27,-68)).arc((40,50),(-72,-7)).assemble().finalize().extrude(-105))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00814137.step')
