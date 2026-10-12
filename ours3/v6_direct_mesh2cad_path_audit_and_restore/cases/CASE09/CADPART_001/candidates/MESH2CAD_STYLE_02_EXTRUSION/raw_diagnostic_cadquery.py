from cadquery import Workspace, Solid
from cadquery import Mesh

# Load mesh data
mesh = Mesh.from_obj(canonical_obj_tokens)

# Create base extrusion
extrusion = Workspace.extrude(mesh, direction='wing_span', length='wing_chord')

# Loft along wing span
lofted_shape = extrusion.loft(direction='wing_span')

# Apply boolean union
final_shape = lofted_shape.boolean_union()

final_shape