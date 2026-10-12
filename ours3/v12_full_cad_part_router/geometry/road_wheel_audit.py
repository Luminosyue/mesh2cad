import numpy as np


def audit_road_wheel(mesh, pattern_consistency=0.0):
    """Measured, deterministic circular evidence. It does not consult semantic IDs."""
    vertices = np.asarray(mesh.vertices, dtype=float)
    center = vertices.mean(axis=0)
    centered = vertices - center
    covariance = np.cov(centered.T)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)
    values, vectors = values[order], vectors[:, order]
    axis = vectors[:, 0]
    axial = centered @ axis
    radial_vectors = centered - np.outer(axial, axis)
    radii = np.linalg.norm(radial_vectors, axis=1)
    mean_radius = float(np.mean(radii))
    radial_cv = float(np.std(radii) / max(mean_radius, 1e-12))
    thickness = float(np.ptp(axial))
    thickness_radius_ratio = thickness / max(2.0 * mean_radius, 1e-12)
    section_circularity = float(max(0.0, 1.0 - radial_cv))
    radial_consistency = float(max(0.0, 1.0 - min(radial_cv / 0.35, 1.0)))
    eig_ratio = float(values[0] / max(values[-1], 1e-12))
    cylinder_supported = bool(
        radial_cv <= 0.12
        and thickness_radius_ratio <= 0.70
        and section_circularity >= 0.88
        and radial_consistency >= 0.65
        and pattern_consistency >= 0.65
    )
    revolution_supported = bool(
        radial_cv <= 0.18
        and section_circularity >= 0.82
        and radial_consistency >= 0.45
        and pattern_consistency >= 0.65
    )
    return {
        "candidate_axis": axis.tolist(),
        "principal_values": values.tolist(),
        "smallest_largest_eigen_ratio": eig_ratio,
        "mean_radius": mean_radius,
        "radius_variance": float(np.var(radii)),
        "circle_fit_residual": radial_cv,
        "section_circularity": section_circularity,
        "thickness": thickness,
        "thickness_radius_ratio": thickness_radius_ratio,
        "normal_radial_consistency": radial_consistency,
        "repetition_consistency": float(pattern_consistency),
        "cylinder_geometry_supported": cylinder_supported,
        "revolution_geometry_supported": revolution_supported,
        "measurement_authority": "VERSIONED_V12_PRE_ROUTE_GEOMETRY_AUDIT",
    }
