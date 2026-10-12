import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,50,0))
w1=cq.Workplane('ZX',origin=(0,37,0))
r=w0.sketch().segment((-57,-86),(-47,-86)).segment((-47,-95)).segment((-32,-95)).segment((-32,-86)).segment((22,-86)).segment((22,-71)).segment((0,-71)).segment((0,-57)).segment((-32,-57)).segment((-32,-14)).segment((-47,-14)).segment((-47,-57)).segment((-57,-57)).close().assemble().finalize().extrude(-97).union(w0.sketch().segment((-57,-86),(-47,-86)).segment((-47,-95)).segment((13,-95)).segment((13,-86)).segment((23,-86)).segment((23,-71)).segment((57,-71)).segment((57,-34)).segment((23,-34)).segment((23,-30)).segment((13,-30)).segment((13,-21)).segment((-47,-21)).segment((-47,-30)).segment((-57,-30)).close().assemble().push([(-40,-58)]).circle(13,mode='s').push([(-25.5,92)]).rect(63,16).push([(-25,92)]).circle(6,mode='s').finalize().extrude(-29)).union(w0.sketch().segment((-57,-13),(-25,-13)).segment((-25,31)).segment((23,1)).segment((37,27)).segment((23,35)).segment((23,55)).segment((1,55)).segment((-51,87)).segment((-57,77)).close().assemble().push([(49,-57)]).circle(24).finalize().extrude(-29)).union(w1.workplane(offset=-87/2).moveTo(-34,-57).box(26,86,87))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00300649.step')
