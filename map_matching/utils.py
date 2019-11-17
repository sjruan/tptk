import networkx as nx
import math
from common.spatial_func import SPoint, distance


def find_shortest_path(rn, prev_candi_pt, cur_candi_pt):
    if nx.is_directed(rn):
        return find_shortest_path_directed(rn, prev_candi_pt, cur_candi_pt)
    else:
        return find_shortest_path_undirected(rn, prev_candi_pt, cur_candi_pt)


def find_shortest_path_directed(rn, prev_candi_pt, cur_candi_pt):
    # case 1, on the same road
    if prev_candi_pt.eid == cur_candi_pt.eid:
        if prev_candi_pt.offset < cur_candi_pt.offset:
            return (cur_candi_pt.offset - prev_candi_pt.offset), []
        else:
            return float('inf'), None
    # case 2, on different roads (including opposite roads)
    else:
        pre_u, pre_v = rn.edge_idx[prev_candi_pt.eid]
        cur_u, cur_v = rn.edge_idx[cur_candi_pt.eid]
        try:
            path = get_shortest_path_with_dist(rn, pre_v, cur_u, rn[pre_u][pre_v]['length'] - prev_candi_pt.offset,
                                               cur_candi_pt.offset, heuristic)
            return path
        except nx.NetworkXNoPath:
            return float('inf'), None


def find_shortest_path_undirected(rn, prev_candi_pt, cur_candi_pt):
    # case 1, on the same road
    if prev_candi_pt.eid == cur_candi_pt.eid:
        return math.fabs(cur_candi_pt.offset - prev_candi_pt.offset), []
    # case 2, on different roads (including opposite roads)
    else:
        pre_u, pre_v = rn.edge_idx[prev_candi_pt.eid]
        cur_u, cur_v = rn.edge_idx[cur_candi_pt.eid]
        min_dist = float('inf')
        shortest_path = None
        paths = []
        # prev_u -> cur_u
        try:
            paths.append(get_shortest_path_with_dist(rn, pre_u, cur_u, prev_candi_pt.offset,
                                                     cur_candi_pt.offset, heuristic))
        except nx.NetworkXNoPath:
            pass
        # prev_u -> cur_v
        try:
            paths.append(get_shortest_path_with_dist(rn, pre_u, cur_v, prev_candi_pt.offset,
                                                     rn[cur_u][cur_v]['length']-cur_candi_pt.offset, heuristic))
        except nx.NetworkXNoPath:
            pass
        # pre_v -> cur_u
        try:
            paths.append(get_shortest_path_with_dist(rn, pre_v, cur_u, rn[pre_u][pre_v]['length']-prev_candi_pt.offset,
                                                     cur_candi_pt.offset, heuristic))
        except nx.NetworkXNoPath:
            pass
        # prev_v -> cur_v:
        try:
            paths.append(get_shortest_path_with_dist(rn, pre_v, cur_v, rn[pre_u][pre_v]['length']-prev_candi_pt.offset,
                                                     rn[cur_u][cur_v]['length']-cur_candi_pt.offset, heuristic))
        except nx.NetworkXNoPath:
            pass
        if len(paths) > 0:
            min_dist, shortest_path = min(paths, key=lambda t: t[0])
        return min_dist, shortest_path


def heuristic(node1, node2):
    return distance(SPoint(node1[1], node1[0]), SPoint(node2[1], node2[0]))


def get_shortest_path_with_dist(rn, src, dest, dist_to_src, dist_to_dest, heuristic):
    dist = 0.0
    path = nx.astar_path(rn, src, dest, heuristic, weight='length')
    dist += dist_to_src
    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]
        dist += rn[start][end]['length']
    dist += dist_to_dest
    return dist, path


def to_wkt(coords):
    wkt = 'LINESTRING ('
    for coord in coords:
        wkt += '{} {}, '.format(coord.lng, coord.lat)
    wkt = wkt[:-2] + ')'
    return wkt
