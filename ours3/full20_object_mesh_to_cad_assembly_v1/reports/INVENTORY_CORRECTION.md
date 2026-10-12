# Explicit completeness correction

{
  "reason": "n_xpart_parts counted successful subset, not original complete part set. Correct expected count uses P3 files, num_parts, and XPART_ATTEMPTED_PARTS; exact ID set equality required.",
  "OBJECT_IDS_CHANGED": false,
  "INITIAL_AUDIT_INVALIDATED": true,
  "SELECTED_OBJECT_N": 20,
  "FULL_INPUT_GATE_PASS_N": 15,
  "TOTAL_EXPECTED_PART_N": 304,
  "EXISTING_XPART_N": 254,
  "MISSING_XPART_N": 50,
  "changes": [
    {
      "OBJECT_ID": "3d_dollhouse_sofa",
      "PREVIOUS_INCORRECT_PART_N": 4,
      "CORRECT_FULL_PART_N": 8,
      "MISSING_XPART_N": 4,
      "SELECTION_REPLACED": false
    },
    {
      "OBJECT_ID": "winerack",
      "PREVIOUS_INCORRECT_PART_N": 4,
      "CORRECT_FULL_PART_N": 34,
      "MISSING_XPART_N": 30,
      "SELECTION_REPLACED": false
    },
    {
      "OBJECT_ID": "mini_fire_engine",
      "PREVIOUS_INCORRECT_PART_N": 7,
      "CORRECT_FULL_PART_N": 16,
      "MISSING_XPART_N": 9,
      "SELECTION_REPLACED": false
    },
    {
      "OBJECT_ID": "dvd_player",
      "PREVIOUS_INCORRECT_PART_N": 6,
      "CORRECT_FULL_PART_N": 7,
      "MISSING_XPART_N": 1,
      "SELECTION_REPLACED": false
    },
    {
      "OBJECT_ID": "assorted_vegetable_set",
      "PREVIOUS_INCORRECT_PART_N": 5,
      "CORRECT_FULL_PART_N": 11,
      "MISSING_XPART_N": 6,
      "SELECTION_REPLACED": false
    }
  ],
  "original_manifest_preserved": "/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/manifests/initial_incorrect_count_audit",
  "timestamp": 1790302009.7955265
}

The same 20 object identities remain frozen. No runtime-failed object is replaced. Five objects are retained as full-input-gate failures unless their original missing X-Part assets are recovered. Partial assemblies are not valid complete demos.
