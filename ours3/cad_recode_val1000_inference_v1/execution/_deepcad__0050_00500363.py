import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().segment((-25,-80),(-19,-83)).segment((24,0)).segment((18,3)).close().assemble().finalize().extrude(6).union(w0.sketch().segment((-52,-99),(-50,-100)).segment((16,20)).segment((16,19)).segment((17,19)).segment((36,-50)).segment((49,-46)).segment((46,-37)).segment((52,-37)).segment((53,58)).segment((45,58)).segment((45,60)).segment((23,69)).segment((15,50)).segment((-48,100)).segment((-48,99)).segment((-1,63)).segment((-29,-2)).segment((-37,-2)).segment((-37,-5)).segment((-21,-5)).segment((-19,-15)).segment((10,-22)).close().assemble().finalize().extrude(28))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00500363.step')
