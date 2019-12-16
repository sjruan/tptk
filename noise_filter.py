from common.spatial_func import distance
from common.trajectory import Trajectory


class NoiseFilter:
    def filter(self, traj):
        pass

    def get_tid(self, oid, clean_pt_list):
        return oid + '_' + clean_pt_list[0].time.strftime('%Y%m%d%H%M') + '_' + \
               clean_pt_list[-1].time.strftime('%Y%m%d%H%M')


class HeuristicFilter(NoiseFilter):
    def __init__(self, max_speed):
        super(NoiseFilter, self).__init__()
        self.max_speed = max_speed

    def filter(self, traj):
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return None
        pre_pt = pt_list[0]
        clean_pt_list = [pre_pt]
        for cur_pt in pt_list[1:]:
            time_span = (cur_pt.time - pre_pt.time).total_seconds()
            dist = distance(pre_pt, cur_pt)
            if time_span > 0 and dist / time_span <= self.max_speed:
                clean_pt_list.append(cur_pt)
                pre_pt = cur_pt
        if len(clean_pt_list) > 1:
            return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
        else:
            return None


class STFilter(NoiseFilter):
    def __init__(self, mbr, start_time, end_time):
        super(STFilter, self).__init__()
        self.mbr = mbr
        self.start_time = start_time
        self.end_time = end_time

    def filter(self, traj):
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return None
        clean_pt_list = []
        for pt in pt_list:
            if self.start_time <= pt.time < self.end_time and self.mbr.contains(pt.lat, pt.lng):
                clean_pt_list.append(pt)
        if len(clean_pt_list) > 1:
            return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
        else:
            return None
