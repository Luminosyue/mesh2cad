from .part_route_state import PartRouteStatus


class FullCADPartRouter:
    def __init__(self, route_callback):
        self.route_callback = route_callback

    def route_case(self, case_context):
        results = []
        for part in case_context["parts"]:
            try:
                result = self.route_callback(case_context, part)
            except Exception as exc:
                result = {
                    "case_id": case_context["case_id"],
                    "part_id": part["part_id"],
                    "semantic_role": part.get("semantic_role", "UNKNOWN"),
                    "status": PartRouteStatus.INTERNAL_ERROR.value,
                    "blocker": f"{type(exc).__name__}:{exc}",
                    "fresh_brep": False,
                    "historical_step_reused": False,
                    "runtime_remeasurement": False,
                }
            if result.get("status") not in PartRouteStatus.terminal_values():
                raise ValueError(f"NON_TERMINAL_STATUS:{result.get('status')}")
            results.append(result)
        return {
            "case_id": case_context["case_id"],
            "parts_total": len(case_context["parts"]),
            "parts_routed": len(results),
            "part_route_coverage": len(results) / max(len(case_context["parts"]), 1),
            "per_part_results": results,
        }
