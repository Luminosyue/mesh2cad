# CAD_RENDER_V4_REPORT

Rendered 20 existing V3 assemblies. The source STEP and part transforms are identical to V3. Per-part STEP hashes before/after match. This branch performs no fitting and changes no metrics, acceptance threshold or status.

V3 sampled tessellated triangles with their constant face normals. V4 tessellates original STEP for display at adaptive linear deflection (camera span * 0.00025 / world scale), angular deflection 0.025 radians, and uses exact OCC surface normals at display vertices. VTK Phong interpolation provides smooth within-face shading. Vertices are not merged across B-Rep faces, so true sharp edges retain separate normals. No smoothing-angle heuristic is needed or applied; tangent continuity comes from the underlying surface normals. All real edges can be overlaid from STEP topology. Tessellation triangle wireframe is disabled.

Camera matrix, object center, span, orthographic scale and vertical image offset match V3. Previous polygonal-profile planar sidewalls remain genuine planar geometry; smoothing the display does not turn them into a curved B-Rep. This is expected and is addressed only by the separate fitting branch.

SMOOTH_SHADING_ENABLED = YES
BREP_EDGE_OVERLAY_AVAILABLE = YES
TRIANGLE_EDGE_DISPLAY_DISABLED = YES
HIGH_QUALITY_TESSELLATION = YES
GEOMETRY_CHANGED_BY_RENDERER = NO
REPRESENTATIVE_RENDER_N = 20

All previews include historical Near/Reject candidates. No assembly optimization or full-object quality acceptance is claimed. Detailed geometry hashes and display settings: renders/*/manifest.json and config/render_v4.json.

## Visual QA

Toaster, robot and kettle comparisons were inspected. Point-sampling grain is removed, analytic face shading is smooth, and actual polygonal/segmented native geometry remains visible. Curved B-Rep overlay edges use 300 samples and straight edges use 2, with a small display-only line depth offset to reduce coincident-surface artifacts. No triangle wireframe is displayed.
