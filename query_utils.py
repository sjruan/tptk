from .common.mbr import MBR
from .common.spatial_func import LAT_PER_METER, LNG_PER_METER, distance


def query_stay_points_by_temporal_range(sps, start_time, end_time):
    results = []
    # start_time inclusive, end_time exclusive
    for sp in sps:
        if start_time <= sp.get_mid_time() < end_time:
            results.append(sp)
    return results


def query_stay_points_by_spatio_temporal_range(sps, query_pt, start_time, end_time, query_radius, refine=True,
                                               method='mid'):
    results = []
    query_mbr = MBR(query_pt.lat - query_radius * LAT_PER_METER,
                    query_pt.lng - query_radius * LNG_PER_METER,
                    query_pt.lat + query_radius * LAT_PER_METER,
                    query_pt.lng + query_radius * LNG_PER_METER)
    for sp in sps:
        sp_centroid = sp.get_centroid()
        if method == 'mid':
            if query_mbr.contains(sp_centroid.lat, sp_centroid.lng) and start_time <= sp.get_mid_time() < end_time:
                results.append(sp)
        elif method == 'first':
            if query_mbr.contains(sp_centroid.lat, sp_centroid.lng) and start_time <= sp.pt_list[0].time < end_time:
                results.append(sp)
    if refine:
        results = [sp for sp in results if distance(query_pt, sp.get_centroid()) <= query_radius]
    return results
