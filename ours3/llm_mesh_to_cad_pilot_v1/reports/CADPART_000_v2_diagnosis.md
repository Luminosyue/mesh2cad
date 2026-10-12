# CADPART_000 V2 Diagnosis

- STEP reload and tessellation pass, so the work-scale transform fixed the V1 kernel-tolerance failure.
- The reconstructed transverse bbox is too wide because the global spline overshoots between the neck, shoulder, barrel, and cap control points.
- Mean bbox relative error is 0.133125 and surface area ratio is 1.121552; both indicate an oversized radial envelope rather than a missing axial extent.
- Chamfer-L1 is 0.018914 of the source maximum extent. Normal consistency remains high at 0.928409, supporting retention of the REVOLVE route.
- IoU is 0.451371. V3 should reduce barrel radius and replace the long unconstrained spline with explicit line segments plus a local cap spline.
- Source watertightness is valid, but the normalized STL tessellation is reported non-watertight by trimesh, so volume ratio is unavailable rather than fabricated.

