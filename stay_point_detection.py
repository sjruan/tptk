from .common.trajectory import Trajectory, get_tid
from .common.spatial_func import distance


def find_first_exceed_max_distance(pt_list, cur_idx, max_distance):
    cur_pt = pt_list[cur_idx]
    next_idx = cur_idx + 1
    # find all successors whose distance is within MaxStayDist w.r.t. anchor
    while next_idx < len(pt_list):
        next_pt = pt_list[next_idx]
        dist = distance(cur_pt, next_pt)
        if dist > max_distance:
            break
        next_idx += 1
    return next_idx


def exceed_max_time(pt_list, cur_idx, next_idx, max_stay_time):
    '''

    :param pt_list:
    :param cur_idx:
    :param next_idx: next idx is the first idx that outside the distance threshold
    :param max_stay_time:
    :return:
    '''
    time_span = (pt_list[next_idx - 1].time - pt_list[cur_idx].time).total_seconds()
    # the time span is larger than maxStayTimeInSecond, a stay point is detected
    return time_span > max_stay_time


class StayPointDetector:
    def __init__(self, max_stay_dist_in_meter, max_stay_time_in_second):
        self.max_distance = max_stay_dist_in_meter
        self.max_stay_time = max_stay_time_in_second

    def detect(self, traj):
        pass


class StayPointClassicDetector(StayPointDetector):
    def __init__(self, max_stay_dist_in_meter, max_stay_time_in_second):
        super(StayPointClassicDetector, self).__init__(max_stay_dist_in_meter, max_stay_time_in_second)

    def detect(self, traj):
        sp_list = []
        oid = traj.oid
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return sp_list
        cur_idx = 0
        while cur_idx < len(pt_list) - 1:
            next_idx = find_first_exceed_max_distance(pt_list, cur_idx, self.max_distance)
            if exceed_max_time(pt_list, cur_idx, next_idx, self.max_stay_time):
                sp_list.append(Trajectory(oid, get_tid(oid, pt_list[cur_idx:next_idx]), pt_list[cur_idx:next_idx]))
                cur_idx = next_idx
            else:
                cur_idx += 1
        return sp_list


class StayPointDensityDetector(StayPointDetector):
    def __init__(self, max_stay_dist_in_meter, max_stay_time_in_second):
        super(StayPointDensityDetector, self).__init__(max_stay_dist_in_meter, max_stay_time_in_second)

    def detect(self, traj):
        sp_list = []
        oid = traj.oid
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return sp_list
        cur_idx = 0
        furthest_next_idx = float('-inf')
        sp_start_idx = float('-inf')
        is_open = False
        while cur_idx < len(pt_list) - 1:
            next_idx = find_first_exceed_max_distance(pt_list, cur_idx, self.max_distance)
            if furthest_next_idx < next_idx and exceed_max_time(pt_list, cur_idx, next_idx, self.max_stay_time):
                if not is_open:
                    sp_start_idx = cur_idx
                    is_open = True
                # the next idx is expended
                furthest_next_idx = next_idx
            if is_open and cur_idx == furthest_next_idx - 1:
                is_open = False
                sp_list.append(
                    Trajectory(oid, get_tid(oid, pt_list[sp_start_idx:furthest_next_idx]),
                               pt_list[sp_start_idx:furthest_next_idx]))
            cur_idx += 1
        return sp_list
