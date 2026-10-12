#!/usr/bin/env python3
import importlib.util

path = "/data/home/cuiyuehan/project/mesh2cad/ours3/batch9_fullstack_mesh2cad_mac_v6/scripts/batch9_mac.py"
spec = importlib.util.spec_from_file_location("batch9_mac", path)
mac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mac)
client, _, _, _ = mac.make_clients()
for model in ("qwen3.7-max-2026-05-17", "qwen3.7-max", "qwen3.8-max", "qwen3.7-plus", "deepseek-v4-flash"):
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.0,
            max_tokens=128,
            messages=[{"role": "user", "content": "Return exactly: HEALTH_OK"}],
        )
        content = response.choices[0].message.content or ""
        print(f"MODEL={model} HTTP=200 NONEMPTY={bool(content.strip())} RESPONSE={content.strip()[:80]!r}")
    except Exception as exc:
        code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        print(f"MODEL={model} HTTP={code} ERROR={type(exc).__name__}: {str(exc)[:240]}")
