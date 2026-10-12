# Tank PART_029 demo result

`case_014` is the Tank object `PART_029`. Its Demo5 teacher-forcing scan reached zero errors at checkpoint 160. The empty-target greedy free rollout produced 1,529 q values with natural `E` and an exact match to the canonical V3 q stream.

The generated V3 was parsed and compiled to a valid CadQuery BRep, exported to STEP, and read back successfully. Generated and canonical volumes were both `0.0029568190049903244`, with absolute volume error `0.0`.
