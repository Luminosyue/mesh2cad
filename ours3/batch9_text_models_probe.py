#!/usr/bin/env python3
import importlib.util

path = "/data/home/cuiyuehan/project/mesh2cad/ours3/batch9_fullstack_mesh2cad_mac_v6/scripts/batch9_mac.py"
spec = importlib.util.spec_from_file_location("batch9_mac", path)
mac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mac)
client, _, configured_model, _ = mac.make_clients()
models = client.models.list()
print("CONFIGURED_TEXT_MODEL=" + configured_model)
for model in sorted(item.id for item in models.data):
    print("MODEL=" + model)
