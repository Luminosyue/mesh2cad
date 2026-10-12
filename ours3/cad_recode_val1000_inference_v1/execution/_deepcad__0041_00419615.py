import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-100,-22),(-94,-22)).segment((-94,-37)).segment((-65,-37)).segment((-65,-34)).arc((-55,-34),(-45,-31)).segment((-45,-37)).segment((-17,-37)).segment((-17,-36)).segment((-14,-36)).segment((-14,-37)).segment((14,-37)).segment((14,-22)).segment((19,-22)).segment((19,-29)).segment((38,-29)).segment((38,-37)).segment((53,-37)).segment((53,-32)).segment((85,-37)).segment((100,32)).segment((62,37)).segment((62,32)).segment((53,32)).segment((53,33)).segment((38,33)).segment((38,32)).segment((19,32)).segment((19,37)).segment((-19,37)).segment((-19,22)).segment((-28,22)).arc((-49,32),(-72,35)).segment((-72,37)).segment((-100,37)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00419615.step')
