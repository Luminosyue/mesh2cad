import argparse
import json
from build123d import Vector, Polyline, make_face, loft, export_step

def main():
    parser = argparse.ArgumentParser(description="Loft CAD part from JSON spec.")
    parser.add_argument("--spec", required=True, help="Path to the JSON spec file.")
    parser.add_argument("--output", required=True, help="Path to the output STEP file.")
    args = parser.parse_args()

    with open(args.spec, "r") as f:
        spec = json.load(f)

    sections = spec["operations"][0]["sections"]

    if len(sections) != 14:
        raise ValueError(f"Expected exactly 14 sections, got {len(sections)}")

    faces = []
    for section in sections:
        y_coord = section["coordinate"]
        profile = section["profile"]

        if len(profile) != 8:
            raise ValueError(f"Expected exactly 8 vertices per profile, got {len(profile)}")

        # Map [x, z] to Vector(x, y, z)
        pts = [Vector(p[0], y_coord, p[1]) for p in profile]

        # Create a closed Wire and then a planar Face
        wire = Polyline(*pts, close=True)
        face = make_face(wire)
        faces.append(face)

    # Execute global loft operation
    solid = loft(faces, ruled=False)

    # Export to STEP
    export_step(solid, args.output)

if __name__ == "__main__":
    main()
