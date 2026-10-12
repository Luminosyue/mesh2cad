"""Contract checks shared by the exhaustive small-DAG V7D1 solver."""
def station_monotone(path):
    values=[node['station_s'] for node in path]
    return all(b>=a for a,b in zip(values,values[1:]))
def production_allowed(track_status): return track_status in {'HIGH','MEDIUM'}
