from cadquery import Workspace
from cadquery import Base
from cadquery import Mesh
from cadquery import Extrusion

# Define plane from mesh
plane = Workspace().plane()

# Define extrusion profile
profile = plane.addPolygon([(0, 0), (0.37, 0), (0.37, 0.15), (0, 0.15)])

# Extrude profile
wing = Extrusion(profile, 0.02)

# Return wing
wing