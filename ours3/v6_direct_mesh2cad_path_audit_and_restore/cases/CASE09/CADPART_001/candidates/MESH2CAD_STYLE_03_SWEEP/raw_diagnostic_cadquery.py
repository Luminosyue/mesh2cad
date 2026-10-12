from cadquery import Workspace, Solid
from cadquery import Mesh

# Load mesh data
mesh = Mesh.from_obj(canonical_obj_tokens)

# Create swept surface
swept = Workspace.sweep(mesh, direction='wing_span', length='wing_chord')

# Extrude swept surface
extruded = swept.extrude(direction='wing_span', length='wing_chord')

# Apply boolean union
final_shape = extruded.boolean_union()

final_shape