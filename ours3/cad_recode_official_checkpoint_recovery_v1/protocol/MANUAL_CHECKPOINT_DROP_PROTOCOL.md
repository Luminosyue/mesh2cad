# Manual checkpoint drop protocol

Allowed source: exact official Hugging Face snapshot `filapro/cad-recode-v1.5`, copied from a networked trusted environment to `/data/home/cuiyuehan/project/mesh2cad/ours3/external_checkpoints/cad_recode_v1_5/`. Preserve all config, tokenizer, and model files. Record repo id, revision, file inventory, total size, and SHA256 for every file. Verify snapshot metadata before loading. Third-party or unknown weights are prohibited.

After verification, rerun only the frozen case `deepcad__0009_00095135` with the official runner and no GT-dependent alignment.
