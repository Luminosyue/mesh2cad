from cadquery import Workspace, Solid
from cadquery import Mesh

# Load mesh data
mesh = Mesh.from_obj(canonical_obj_tokens)

# Create lofted surface
lofted = Workspace.loft(mesh, direction='wing_span', length='wing_chord')

# Extrude lofted surface
extruded = lofted.extrude(direction='wing_span', length='wing_chord')

# Apply boolean union
final_shape = extruded.boolean_union()

final_shape