import cadquery as cq

# ==============================
# Dimension definitions (max 100 units)
# ==============================
# Sheet overall size
sheet_width = 80.0          # X dimension (total width)
sheet_depth = 60.0          # Y dimension (total depth)
sheet_thickness = 2.0       # Z thickness of the cold‑rolled sheet
# Edge treatment
outer_fillet_radius = 0.5   # Fillet applied to the outer perimeter (must be < thickness)
# X‑mount socket
socket_arm_width = 12.0      # Width of each X‑mount arm
socket_arm_length = 20.0     # Half‑length of each arm from centre (total arm length = 2*20)
socket_center_offset_y = 30.0  # Y offset of socket centre from sheet front edge
socket_cut_depth = sheet_thickness + 5.0  # Depth of the socket recess
# Peripheral keyway (slot along side)
keyway_width = 8.0
keyway_depth = sheet_thickness + 1.0
keyway_offset_y = 5.0        # Distance from front edge to keyway centre
# Notch cutout (adds composite profile complexity)
notch_width = 12.0
notch_height = 6.0
notch_margin = 2.0           # Distance from outer edge to notch start
# Chamfer for socket entry edges
socket_entry_chamfer = 0.5

# ==============================
# Base sheet creation (composite profile with a corner notch)
# ==============================
base_sheet = (
    cq.Workplane("XY")
    .rect(sheet_width, sheet_depth)          # centered rectangle
    .extrude(sheet_thickness)
)
# Cut a rectangular notch at the right‑hand front corner to increase profile complexity
notch = (
    cq.Workplane("XY")
    .center(
        sheet_width / 2 - notch_margin - notch_width / 2,
        -sheet_depth / 2 + notch_margin + notch_height / 2,
    )
    .rect(notch_width, notch_height)
    .extrude(sheet_thickness)
)
base_with_notch = base_sheet.cut(notch)
# Apply fillet to the outer perimeter (excluding the notch edges)
base_fillet = (
    base_with_notch
    .edges("<Z")
    .fillet(outer_fillet_radius)
)

# ==============================
# X‑mount socket creation (cross‑shaped recess)
# ==============================
# Horizontal arm of the X
socket_horiz = (
    cq.Workplane("XY")
    .center(0, socket_center_offset_y - sheet_depth / 2)  # shift to sheet local coordinates
    .rect(socket_arm_width, 2 * socket_arm_length)
    .extrude(-socket_cut_depth)
)
# Vertical arm (rotated 90°)
socket_vert = (
    cq.Workplane("XY")
    .center(0, socket_center_offset_y - sheet_depth / 2)
    .rect(2 * socket_arm_length, socket_arm_width)
    .extrude(-socket_cut_depth)
)
# Combine arms to form X shape
socket_union = socket_horiz.union(socket_vert)
# Chamfer the entry edges of the socket (edges that intersect the top surface)
socket_chamfered = (
    socket_union
    .edges(">Z and (|X or |Y)")
    .chamfer(socket_entry_chamfer)
)
# Subtract socket from sheet
sheet_with_socket = base_fillet.cut(socket_chamfered)

# ==============================
# Peripheral keyway creation (slot along the left side)
# ==============================
keyway = (
    cq.Workplane("XY")
    .center(
        -sheet_width / 2 + keyway_width / 2 + notch_margin,  # keep a small margin from outer edge
        keyway_offset_y - sheet_depth / 2,
    )
    .rect(keyway_width, keyway_depth)
    .extrude(-sheet_thickness - 0.5)  # cut slightly deeper than sheet thickness
)
# Subtract keyway
result = sheet_with_socket.cut(keyway)
