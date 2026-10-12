from cadquery import Workspace, Solid
from cadquery import Mesh

# Load mesh data
mesh = Mesh.from_obj(canonical_obj_tokens)

# Create base plane
plane = Workspace.plane()

# Extrude mesh along wing span
extrusion = plane.extrude(mesh, direction='wing_span', length='wing_chord')

# Apply boolean union
final_shape = extrusion.boolean_union()

final_shape