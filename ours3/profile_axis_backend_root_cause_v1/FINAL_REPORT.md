# Profile/Axis Backend Root Cause V1

`CURRENT_GATE=PROFILE_AXIS_ROOT_CAUSE_IDENTIFIED`

The shared blocker is incomplete recovery of sketch-local geometry into a global CAD frame, combined with missing canonical profile loop membership. FeatureScript contains entity parameters and query provenance, but the current converter retains only stable IDs and drops executable geometry/topology before the backend. Axis references are predominantly sketch-line derived; no global or numeric axis evidence was found in the frozen canary.

No formal converter, parser, executor, geometry gate, model, or Placement branch was modified. The next implementation target is a combined sketch-geometry runtime that extracts source entities, preserves loop membership, applies the source frame, and resolves entity-derived axes before re-running the same Canary10.
