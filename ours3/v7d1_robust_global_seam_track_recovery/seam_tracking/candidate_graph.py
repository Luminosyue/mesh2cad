"""Monotone endpoint-pair DAG primitives."""
def edges_between_layers(layers,max_skip=2):
    edges=[]
    for i,layer in enumerate(layers):
        for j in range(i+1,min(len(layers),i+max_skip+2)):
            edges.extend((a,b,j-i-1) for a in layer for b in layers[j])
    return edges
def is_dag_edge(source,target): return target['station_index']>source['station_index']
