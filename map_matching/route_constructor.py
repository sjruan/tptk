from .utils import find_shortest_path
from datetime import timedelta
import networkx as nx
from ..common.path import PathEntity, Path


def construct_path(rn, mm_traj, routing_weight):
    """
    construct the path of the map matched trajectory
    Note: the enter time of the first path entity & the leave time of the last path entity is not accurate
    :param rn: the road network
    :param mm_traj: the map matched trajectory
    :param routing_weight: the attribute name to find the routing weight
    :return: a list of paths (Note: in case that the route is broken)
    """
    paths = []
    path = []
    mm_pt_list = mm_traj.pt_list
    start_idx = len(mm_pt_list) - 1
    # find the first matched point
    for i in range(len(mm_pt_list)):
        if mm_pt_list[i].data['candi_pt'] is not None:
            start_idx = i
            break
    pre_edge_enter_time = mm_pt_list[start_idx].time
    for i in range(start_idx + 1, len(mm_pt_list)):
        pre_mm_pt = mm_pt_list[i-1]
        cur_mm_pt = mm_pt_list[i]
        # unmatched -> matched
        if pre_mm_pt.data['candi_pt'] is None:
            pre_edge_enter_time = cur_mm_pt.time
            continue
        # matched -> unmatched
        pre_candi_pt = pre_mm_pt.data['candi_pt']
        if cur_mm_pt.data['candi_pt'] is None:
            path.append(PathEntity(pre_edge_enter_time, pre_mm_pt.time, pre_candi_pt.eid))
            if len(path) > 2:
                paths.append(Path(mm_traj.oid, get_pid(mm_traj.oid, path), path))
            path = []
            continue
        # matched -> matched
        cur_candi_pt = cur_mm_pt.data['candi_pt']
        # if consecutive points are on the same road, cur_mm_pt doesn't bring new information
        if pre_candi_pt.eid != cur_candi_pt.eid:
            weight_p, p = find_shortest_path(rn, pre_candi_pt, cur_candi_pt, routing_weight)
            # cannot connect
            if p is None:
                path.append(PathEntity(pre_edge_enter_time, pre_mm_pt.time, pre_candi_pt.eid))
                if len(path) > 2:
                    paths.append(Path(mm_traj.oid, get_pid(mm_traj.oid, path), path))
                path = []
                pre_edge_enter_time = cur_mm_pt.time
                continue
            # can connect
            if nx.is_directed(rn):
                dist_to_p_entrance = rn.edges[rn.edge_idx[pre_candi_pt.eid]]['length'] - pre_candi_pt.offset
                dist_to_p_exit = cur_candi_pt.offset
            else:
                entrance_vertex = p[0]
                pre_edge_coords = rn.edges[rn.edge_idx[pre_candi_pt.eid]]['coords']
                if (pre_edge_coords[0].lng, pre_edge_coords[0].lat) == entrance_vertex:
                    dist_to_p_entrance = pre_candi_pt.offset
                else:
                    dist_to_p_entrance = rn.edges[rn.edge_idx[pre_candi_pt.eid]]['length'] - pre_candi_pt.offset
                exit_vertex = p[-1]
                cur_edge_coords = rn.edges[rn.edge_idx[cur_candi_pt.eid]]['coords']
                if (cur_edge_coords[0].lng, cur_edge_coords[0].lat) == exit_vertex:
                    dist_to_p_exit = cur_candi_pt.offset
                else:
                    dist_to_p_exit = rn.edges[rn.edge_idx[cur_candi_pt.eid]]['length'] - pre_candi_pt.offset
            if routing_weight == 'length':
                total_dist = weight_p
            else:
                dist_inner = 0.0
                for i in range(len(p) - 1):
                    start, end = p[i], p[i + 1]
                    dist_inner += rn[start][end]['length']
                total_dist = dist_inner + dist_to_p_entrance + dist_to_p_exit
            delta_time = (cur_mm_pt.time - pre_mm_pt.time).total_seconds()
            # two consecutive points matched to the same vertex
            if total_dist == 0:
                pre_edge_leave_time = cur_mm_pt.time
                path.append(PathEntity(pre_edge_enter_time, pre_edge_leave_time, pre_candi_pt.eid))
                cur_edge_enter_time = cur_mm_pt.time
            else:
                pre_edge_leave_time = pre_mm_pt.time + timedelta(seconds=delta_time*(dist_to_p_entrance/total_dist))
                path.append(PathEntity(pre_edge_enter_time, pre_edge_leave_time, pre_candi_pt.eid))
                cur_edge_enter_time = cur_mm_pt.time - timedelta(seconds=delta_time * (dist_to_p_exit / total_dist))
                sub_path = linear_interpolate_path(p, total_dist - dist_to_p_entrance - dist_to_p_exit,
                                                   rn, pre_edge_leave_time, cur_edge_enter_time)
                path.extend(sub_path)
            pre_edge_enter_time = cur_edge_enter_time
    # handle last matched similar to (matched -> unmatched)
    if mm_pt_list[-1].data['candi_pt'] is not None:
        path.append(PathEntity(pre_edge_enter_time, mm_pt_list[-1].time, mm_pt_list[-1].data['candi_pt'].eid))
        if len(path) > 2:
            paths.append(Path(mm_traj.oid, get_pid(mm_traj.oid, path), path))
    return paths


def linear_interpolate_path(p, dist_inner, rn, enter_time, leave_time):
    path = []
    edges = []
    for i in range(len(p)-1):
        edges.append((p[i], p[i+1]))
    delta_time = (leave_time - enter_time).total_seconds()
    edge_enter_time = enter_time
    for i in range(len(edges)):
        edge_data = rn.edges[edges[i]]
        if i == len(edges) - 1:
            # to make sure the last connect edge leave time
            # meet the path leave time due to double calculation accuracy
            edge_leave_time = leave_time
        else:
            edge_leave_time = edge_enter_time + timedelta(seconds=delta_time*(edge_data['length']/dist_inner))
        path.append(PathEntity(edge_enter_time, edge_leave_time, edge_data['eid']))
        edge_enter_time = edge_leave_time
    return path


def get_pid(oid, path):
    return oid + '_' + path[0].enter_time.strftime('%Y%m%d%H%M') + '_' + \
           path[-1].leave_time.strftime('%Y%m%d%H%M')
