from .common.mbr import MBR
from .common.spatial_func import LAT_PER_METER, LNG_PER_METER, distance
from datetime import timedelta


def query_stay_points_by_temporal_range(sps, start_time, end_time, temporal_relation='middle'):
    results = []
    # start_time inclusive, end_time exclusive
    for sp in sps:
        if is_temporal_valid(sp, start_time, end_time, temporal_relation):
            results.append(sp)
    return results


def query_stay_points_by_spatial_range(sps, start_time, end_time, spatial_relation='centroid'):
    results = []
    # start_time inclusive, end_time exclusive
    for sp in sps:
        if is_spatial_valid(sp, start_time, end_time, spatial_relation):
            results.append(sp)
    return results


def query_stay_points_by_spatio_temporal_range(sps, query_pt, start_time, end_time, query_radius,
                                               spatial_relation='centroid', temporal_relation='middle'):
    results = []
    for sp in sps:
        if is_spatial_valid(sp, query_pt, query_radius, spatial_relation) and \
                is_temporal_valid(sp, start_time, end_time, temporal_relation):
            results.append(sp)
    return results


def is_spatial_valid(sp, query_pt, query_radius, spatial_relation):
    query_mbr = MBR(query_pt.lat - query_radius * LAT_PER_METER,
                    query_pt.lng - query_radius * LNG_PER_METER,
                    query_pt.lat + query_radius * LAT_PER_METER,
                    query_pt.lng + query_radius * LNG_PER_METER)
    if spatial_relation == 'centroid':
        sp_centroid = sp.get_centroid()
        return query_mbr.contains(sp_centroid.lat, sp_centroid.lng) and distance(query_pt, sp.get_centroid()) <= query_radius
    else:
        raise Exception('unknown spatial_relation')


def is_temporal_valid(sp, start_time, end_time, temporal_relation):
    if temporal_relation == 'middle':
        return start_time <= sp.get_mid_time() < end_time
    elif temporal_relation == 'first':
        return start_time <= sp.pt_list[0].time < end_time
    elif temporal_relation == 'intersect':
        return sp.get_start_time() <= start_time < sp.get_end_time() + timedelta(seconds=1) or \
               (start_time <= sp.get_start_time() and end_time > sp.get_end_time()) or \
               sp.get_start_time() <= end_time < sp.get_end_time() + timedelta(seconds=1)
    else:
        raise Exception('unknown temporal_relation')
