def rank_builders(eligibility, role_prior, descriptor, semantic_enabled=True):
    allowed=list(eligibility.get('ALLOWED_BUILDERS') or [])
    rows=[]
    for builder in allowed:
        geom=float((eligibility.get('BUILDER_ELIGIBILITY',{}).get(builder) or {}).get('score') or .5)
        semantic=float(role_prior.get(builder,.15)) if semantic_enabled else .5
        profile=.8 if builder in {'LOFT','GENERAL_BSPLINE'} and descriptor['section_variation']>.08 else .5
        circular=.9 if builder in {'CYLINDER','REVOLUTION'} and (descriptor['disc_likeness']>.35 or descriptor['rod_likeness']>.7) else .45
        complexity=.7 if builder not in {'GENERAL_BSPLINE'} else .55
        score=.43*geom+.27*semantic+.12*profile+.1*circular+.08*complexity
        rows.append({'builder':builder,'geometry_fit_score':geom,'semantic_construction_prior':semantic,
                     'profile_fidelity_proxy':profile,'circular_fidelity_proxy':circular,
                     'complexity_reasonableness':complexity,'score':float(score)})
    return sorted(rows,key=lambda x:(-x['score'],x['builder']))
