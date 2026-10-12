# Restricted CadQuery V1

Allowed calls observed in the discovered cohort:

- `base.union`
- `base.union(plate).union`
- `base.union(plate).union(boss1).union`
- `cq.Workplane`
- `cq.Workplane('XY').polyline`
- `cq.Workplane('XY').polyline([(42, 18), (52, 18), (52, 25), (42, 25)]).close`
- `cq.Workplane('XY').polyline([(42, 18), (52, 18), (52, 25), (42, 25)]).close().revolve`
- `cq.Workplane('XY').polyline(profile).close`
- `cq.Workplane('XY').polyline(profile).close().revolve`
- `solid.cut`
