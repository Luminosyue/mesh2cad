import cadquery as cq
import copy
from types import SimpleNamespace as Measures

def combine_wires(self):
    wires = [obj for obj in self.objects if isinstance(obj, cq.Wire)]
    if len(wires) < 2:
        return self
    combined = None
    for w in wires:
        solid = cq.Workplane('XY').add(w).extrude(0.01)
        combined = solid if combined is None else combined.union(solid)
    result_wire = combined.faces('>Z').wires().val()
    return self.newObject([result_wire])

cq.Workplane.combine_wires = combine_wires

class CutawayXMountHolder:
    def __init__(self, workplane, measures):
        self.workplane = workplane
        self.measures = copy.deepcopy(measures)
        self.build()
    def build(self):
        m = self.measures
        base = (
            cq.Workplane('XY')
            .center(-0.5 * m.base_width, -0.5 * m.base_depth)
            .rect(m.base_width, m.base_depth)
            .extrude(m.base_height)
            .edges('|Z')
            .chamfer(m.base_chamfer)
        )
        pocket_profile = (
            cq.Workplane('XY')
            .center(-0.5 * m.pocket_width, -0.5 * m.pocket_depth)
            .polyline([
                (0, 0),
                (m.pocket_width - m.notch_width, 0),
                (m.pocket_width - m.notch_width, m.notch_depth),
                (m.pocket_width, m.notch_depth),
                (m.pocket_width, m.pocket_depth),
                (0, m.pocket_depth),
                (0, 0),
            ])
            .close()
            .extrude(-m.pocket_height)
            .edges('|Z')
            .chamfer(m.pocket_chamfer)
        )
        socket = (
            cq.Workplane('XY')
            .center(-0.5 * m.socket_width, -0.5 * m.socket_depth)
            .rect(m.socket_width, m.socket_depth)
            .extrude(-m.socket_height)
            .edges('|Z')
            .chamfer(m.socket_chamfer)
        )
        blind_hole = (
            cq.Workplane('XY')
            .center(0, 0)
            .circle(m.blind_hole_diameter / 2)
            .extrude(-m.blind_hole_depth)
        )
        socket_pos = socket.translate((m.pocket_offset_x, m.pocket_offset_y, 0))
        blind_hole_pos = blind_hole.translate((m.blind_hole_offset_x, m.blind_hole_offset_y, -m.pocket_height + m.blind_hole_depth))
        pocket = pocket_profile.cut(socket_pos).cut(blind_hole_pos)
        part = (
            base
            .cut(pocket)
            .edges('|Z')
            .chamfer(m.top_chamfer)
        )
        self.model = part

measures = Measures(
    base_width=80,
    base_depth=60,
    base_height=8,
    base_chamfer=1,
    pocket_width=50,
    pocket_depth=40,
    pocket_height=12,
    pocket_chamfer=0.8,
    notch_width=8,
    notch_depth=4,
    socket_width=30,
    socket_depth=20,
    socket_height=10,
    socket_chamfer=0.5,
    pocket_offset_x=10,
    pocket_offset_y=5,
    blind_hole_diameter=6,
    blind_hole_depth=6,
    blind_hole_offset_x=25,
    blind_hole_offset_y=20,
    top_chamfer=0.5,
)

result = CutawayXMountHolder(cq.Workplane('XY'), measures).model
