import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-37),(-76,-37)).segment((-76,-43)).segment((-63,-43)).segment((-63,-37)).segment((-48,-37)).segment((-48,-16)).segment((-29,-20)).segment((-32,-43)).segment((0,-43)).segment((0,-29)).segment((14,-31)).segment((14,-33)).segment((23,-33)).segment((23,-31)).segment((63,-44)).segment((67,-33)).segment((100,-33)).segment((100,43)).segment((27,43)).segment((27,29)).segment((14,31)).segment((14,33)).segment((13,33)).segment((13,43)).segment((-16,43)).segment((-16,35)).segment((-44,35)).segment((-44,43)).segment((-93,43)).segment((-93,29)).segment((-96,29)).segment((-96,10)).segment((-93,10)).segment((-93,7)).segment((-76,7)).segment((-76,10)).segment((-73,10)).segment((-73,6)).segment((-92,6)).segment((-92,10)).segment((-96,10)).segment((-96,13)).segment((-97,13)).close().assemble().push([(61,10)]).circle(16,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00364491.step')
