from dataclasses import dataclass,asdict
@dataclass
class PrimitiveCandidate:
 surface_id:str; primitive_type:str; parameters:dict; fit_error:dict; validity:dict; provenance:dict
 def to_dict(self):return asdict(self)
