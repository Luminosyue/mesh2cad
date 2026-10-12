import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-93,-38),(-87,-38)).arc((-88,-40),(-88,-42)).segment((-89,-44)).segment((-87,-46)).arc((-78,-60),(-68,-73)).segment((-66,-75)).segment((-65,-74)).arc((-24,-95),(20,-96)).segment((19,-96)).segment((19,-90)).arc((-94,0),(19,90)).segment((19,96)).arc((-1,99),(-19,96)).segment((-20,96)).segment((-20,95)).arc((-81,56),(-93,-22)).close().assemble().reset().face(w0.sketch().arc((33,-93),(45,-87),(56,-81)).segment((57,-81)).segment((57,-79)).arc((76,-63),(91,-40)).segment((90,-38)).arc((91,-36),(91,-34)).segment((93,-32)).segment((91,-30)).arc((82,54),(11,98)).segment((12,96)).arc((8,93),(5,90)).segment((4,92)).arc((-15,92),(-33,88)).segment((-33,87)).arc((-94,0),(-33,-87)).close().assemble()).reset().face(w0.sketch().arc((62,-77),(77,-62),(87,-43)).segment((89,-40)).segment((88,-38)).arc((90,-36),(91,-34)).segment((90,-32)).segment((88,-32)).arc((88,-31),(87,-30)).arc((83,-42),(76,-53)).close().assemble()).finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00583519.step')
