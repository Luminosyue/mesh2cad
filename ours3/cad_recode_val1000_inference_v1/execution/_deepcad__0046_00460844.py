import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(5,0,0))
w1=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((-100,-17),(-92,-21)).segment((-92,-15)).segment((-84,-15)).segment((-84,-20)).segment((-90,-20)).segment((-54,-20)).segment((-54,-19)).segment((-53,-19)).segment((-53,-15)).segment((-57,-15)).segment((-57,14)).segment((-53,14)).segment((-53,15)).segment((-52,15)).segment((-52,14)).segment((-49,14)).segment((-49,-15)).segment((-52,-15)).segment((-52,-16)).segment((-44,-16)).segment((-44,21)).segment((-94,21)).segment((-94,-10)).close().assemble().reset().face(w0.sketch().segment((-37,-20),(6,-20)).segment((6,21)).segment((-12,21)).segment((-12,19)).segment((-19,19)).segment((-19,-13)).segment((-31,-13)).segment((-31,21)).segment((-37,21)).close().assemble()).push([(87,-16)]).circle(13).finalize().extrude(-9).union(w1.workplane(offset=81/2).moveTo(-16,0).cylinder(81,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00460844.step')
