# Goal is to annotate a vertex cover with dictionary representing various cluster metrics 
from igraph import Cover 
from scipy import nansum

def fomd(cover, degree_stats_dict=None):
    '''
    Fraction over median degree is the number of nodes that have an internal degree greater than the median degree of 
    all nodes in the graph.
    '''
    cover.graph.compute_metrics(refresh=False)
    g_metrics = cover.graph.metrics

    median = g_metrics['Degree Statistics']['Median']
    rv = []
    for i in range(len(cover)):
        subgraph = cover.subgraph(i) 
        rv += [sum(1.0 for v in subgraph.degree() if v > median)/subgraph.vcount()]
    return rv 

def expansion(cover):
    '''
    Expansion is the ratio between the number of external (boundary) edges in a cluster and the number of nodes in the cluster.
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        size_i = cover.size(i)
        rv += [1.0*len(external_edges[i])/size_i]
    return rv

def cut_ratio(cover):
    '''
    Cut ratio is the ratio between the number of external (boundary) edges in a cluster and the cluster's maximum possible number of external edges
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        size_i = cover.size(i)
        size_g = cover.graph.vcount()
        rv += [1.0*len(external_edges[i])/(size_i*(size_g-size_i))]
    return rv

def conductance(cover):
    '''
    Conductance is the ratio between the number of external (boundary) edges in a cluster and the cluster's total number of edges
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = cover.subgraph(i).ecount()
        ext_edges_cnt = len(external_edges[i])
        rv += [ext_edges_cnt/(2*int_edges_cnt+ext_edges_cnt)]
    return rv

def separability(cover):
    '''
    Separability is the ratio between the number of internal edges in a cluster and its number of external (boundary) edges.
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = cover.subgraph(i).ecount()
        ext_edges_cnt = len(external_edges[i])
        rv += [1.*int_edges_cnt/ext_edges_cnt]
    return rv


def normalized_cut(cover):
    '''
    Normalized cut is the sum of conductance with the fraction of external edges over all non-cluster edges
    '''
    rv = cover.conductance()
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = cover.subgraph(i).ecount()
        ext_edges_cnt = len(external_edges[i])
        tot_edge_cnt = cover.graph.ecount()
        rv[i] += ext_edges_cnt/(2*(tot_edge_cnt - int_edges_cnt)+ext_edges_cnt)

    return rv

def maximum_out_degree_fraction(cover):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges 
    and its internal edges. Maximum ODF returns the maximum fraction for the cluster.
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            node_index = edge.source if i in cover.membership[edge.source] else edge.target
            ext_edge_per_node[node_index] += 1.0
        ratios = []
        for pair in zip(ext_edge_per_node, degree_per_node):
             ratios += [ pair[0]/pair[1] if pair[1] != 0 else float('nan') ]
        rv += [max(ratios)]
    return rv

def average_out_degree_fraction(cover):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges 
    and its internal edges. Average ODF returns the average fraction for the cluster.
    '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            node_index = edge.source if i in cover.membership[edge.source] else edge.target
            ext_edge_per_node[node_index] += 1.0
        ratios = []
        for pair in zip(ext_edge_per_node, degree_per_node):
            ratios += [ pair[0]/pair[1] if pair[1] != 0 else float('nan') ]
        rv += [nansum(ratios)/cover.subgraph(i).vcount()]
    return rv

def flake_out_degree_fraction(cover):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges 
    and its internal edges. Flake ODF returns the number of nodes for which this ratio is less than 1, i.e. a node has fewer internal edges than external ones.
     '''
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            node_index = edge.source if i in cover.membership[edge.source] else edge.target
            ext_edge_per_node[node_index] += 1.0
        flake = []
        for pair in zip(ext_edge_per_node, degree_per_node):
            flake += [ pair[0] > pair[1]/2.0 ]
        rv += [sum(flake)/cover.subgraph(i).vcount()]
    return rv

def external_edges(cover) :
    '''
    @param cover a VertexCover object.
    @returns an array of external edges per cluster in the cover.
    '''
    array_of_sets = [ [] for v in cover ] 
    #Iterate over crossing edges
    for edge in [ a[1] for a in zip(cover.crossing(), cover.graph.es()) if a[0]]:
        membership = [cover.membership[edge.source]]
        if not cover.graph.is_directed():
            membership += [cover.membership[edge.target]]

        for node_membership in membership: 
            for cluster_id in node_membership:
                array_of_sets[cluster_id] += [edge]

    return array_of_sets

def compute_metrics(cover):
    cover.graph.compute_metrics(refresh=False)
    g_metrics = cover.graph.metrics
    cover.metrics = { 
            'Fraction over a Median Degree' : fomd(cover, g_metrics['Degree Statistics']),
            'Expansion'                     : expansion(cover),
            'Cut Ratio'                     : cut_ratio(cover),    
            'Conductance'                   : conductance(cover),    
            'Normalized Cut'                : normalized_cut(cover),     
            'Maximum Out Degree Fraction'   : maximum_out_degree_fraction(cover), 
            'Average Out Degree Fraction'   : average_out_degree_fraction(cover),
            'Flake Out Degree Fraction'     : flake_out_degree_fraction(cover),
            'Separability'                  : separability(cover),
            'Subgraphs'                     : []
            }

    for i in range(len(cover)):
        sg = cover.subgraph(i)
        sg.compute_metrics(refresh=False)
        cover.metrics['Subgraphs'] += [sg.metrics]


Cover.metrics = None
Cover.compute_metrics = compute_metrics
Cover.external_edges = external_edges
Cover.expansion = expansion
Cover.cut_ratio = cut_ratio
Cover.conductance = conductance
Cover.normalized_cut = normalized_cut
Cover.fraction_over_median_degree = fomd
Cover.maximum_out_degree_fraction = maximum_out_degree_fraction
Cover.average_out_degree_fraction = average_out_degree_fraction
Cover.flake_out_degree_fraction = flake_out_degree_fraction
Cover.separability = separability
