import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-46),(-33,-46)).segment((-33,-41)).segment((-29,-41)).segment((-29,-49)).segment((-12,-49)).segment((-12,-41)).segment((-7,-41)).segment((-7,-43)).segment((23,-43)).segment((23,-41)).segment((27,-41)).segment((27,-37)).segment((62,-50)).segment((68,-32)).segment((66,-32)).segment((66,-28)).segment((72,-28)).segment((79,-8)).segment((99,-8)).segment((99,-28)).segment((100,-28)).segment((100,37)).segment((99,37)).segment((99,10)).segment((79,10)).segment((79,29)).segment((66,29)).segment((66,49)).segment((26,49)).segment((26,37)).segment((23,37)).segment((23,46)).segment((-7,46)).segment((-7,37)).segment((-12,37)).segment((-12,45)).segment((-29,45)).segment((-29,37)).segment((-33,37)).segment((-33,49)).segment((-93,49)).segment((-93,37)).segment((-100,37)).close().assemble().push([(-49,0)]).rect(42,38,mode='s').push([(63,10)]).circle(19,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00615732.step')
