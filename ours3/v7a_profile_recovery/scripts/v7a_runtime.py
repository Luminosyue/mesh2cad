#!/usr/bin/env python3
"""Contract-closed runtime: consumes V7A profiles and never remeasures mesh geometry."""

import argparse, json
from pathlib import Path
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from builders.registry import get_builder


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def validate_profile(profile):
    return (profile.get("profile_type") in {"CLOSED_SOLID_PROFILE", "CLOSED_MULTI_LOOP_PROFILE"}
            and profile.get("source") == "HIGH_POLY_TRIANGLE_PLANE_INTERSECTION"
            and bool(profile.get("closed"))
            and bool(profile.get("smooth_curve", {}).get("valid")))


def execute(measured_spec, construction_plan, output_step, source_mesh=None):
    spec, plan = load(measured_spec), load(construction_plan)
    if plan.get("part_id") != spec.get("part_id"):
        raise ValueError("CONTRACT_VIOLATION part_id mismatch")
    requested = int(plan.get("profile_count", len(spec.get("profiles", []))))
    if requested <= 0 or requested > len(spec.get("profiles", [])):
        raise ValueError("CONTRACT_VIOLATION profile_count")
    profiles = spec["profiles"][:requested]
    if not all(validate_profile(profile) for profile in profiles):
        raise ValueError("INVALID_PROFILE_RUNTIME_REJECTED")
    builder = get_builder(plan["hypothesis"])
    shape = builder.build(spec, profiles, plan)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("invalid candidate BRep")
    output = Path(output_step)
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(output)) != IFSelect_RetDone:
        raise RuntimeError("STEP_EXPORT_FAILED")
    contract = {"requested_hypothesis": plan["hypothesis"], "executed_builder": builder.name,
                "axis_source": "MEASURED_SPEC", "station_source": "MEASURED_SPEC",
                "profile_source": "GEOMETRY_ANALYZER", "requested_profile_count": requested,
                "executed_profile_count": len(profiles), "runtime_profile_remeasurement": False,
                "runtime_axis_remeasurement": False, "runtime_station_regeneration": False,
                "runtime_override_count": 0, "runtime_clamp_count": 0,
                "profile_polyline_is_sampling_only": True,
                "smooth_profile_curve_consumed": True}
    dump(output.parent / "candidate_execution_contract.json", contract)
    return contract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-mesh")
    parser.add_argument("--measured-spec", required=True)
    parser.add_argument("--construction-plan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.measured_spec, args.construction_plan, args.output,
                             args.source_mesh), indent=2))


if __name__ == "__main__":
    main()
