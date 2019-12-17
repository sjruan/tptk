from common.spatial_func import distance, SPoint
from common.mbr import MBR
from map_matching.candidate_point import CandidatePoint
from datetime import datetime


class STPoint(SPoint):
    def __init__(self, lat, lng, time, data=None):
        super(STPoint, self).__init__(lat, lng)
        self.time = time
        self.data = data

    def __str__(self):
        return '({}, {}, {}, {})'.format(self.time.strftime('%Y/%m/%d %H:%M:%S'), self.lat, self.lng, self.data)


class Trajectory:
    def __init__(self, oid, tid, pt_list):
        self.oid = oid
        self.tid = tid
        self.pt_list = pt_list

    def __hash__(self):
        return hash(self.oid + '_' + self.pt_list[0].time.strftime('%Y%m%d%H%M%S') + '_' +
                    self.pt_list[-1].time.strftime('%Y%m%d%H%M%S'))

    def duration(self):
        return (self.pt_list[-1].time - self.pt_list[0].time).total_seconds()

    def length(self):
        if len(self.pt_list) <= 1:
            return 0.0
        else:
            dist = 0.0
            pre_pt = None
            for pt in self.pt_list:
                if pre_pt is None:
                    pre_pt = pt
                else:
                    tmp_dist = distance(pre_pt, pt)
                    dist += tmp_dist
                    pre_pt = pt
            return dist

    def time_interval(self):
        point_time_interval = []
        for pre, cur in zip(self.pt_list[:-1], self.pt_list[1:]):
            point_time_interval.append((cur.time - pre.time).total_seconds())
        return sum(point_time_interval) / len(point_time_interval)

    def distance_interval(self):
        point_dist_interval = []
        for pre, cur in zip(self.pt_list[:-1], self.pt_list[1:]):
            point_dist_interval.append(distance(pre, cur))
        return sum(point_dist_interval) / len(point_dist_interval)

    def mbr(self):
        return MBR.cal_mbr(self.pt_list)

    def get_mid_time(self):
        return self.pt_list[0].time + (self.pt_list[-1].time - self.pt_list[0].time) / 2.0

    def get_center(self):
        return MBR.cal_mbr(self.pt_list).center()

    def get_centroid(self):
        mean_lat = 0.0
        mean_lng = 0.0
        for pt in self.pt_list:
            mean_lat += pt.lat
            mean_lng += pt.lng
        mean_lat /= len(self.pt_list)
        mean_lng /= len(self.pt_list)
        return SPoint(mean_lat, mean_lng)

    def to_wkt(self):
        wkt = 'LINESTRING ('
        for pt in self.pt_list:
            wkt += '{} {}, '.format(pt.lng, pt.lat)
        wkt = wkt[:-2] + ')'
        return wkt

    def __repr__(self):
        return f'Trajectory(oid={self.oid},tid={self.tid})'


def traj_point_dist(traj, pt):
    dists = []
    for t_pt in traj.pt_list:
        dists.append(distance(t_pt, pt))
    return min(dists)


def parse_traj_file(input_path, traj_type='raw', extra_fields=None):
    assert traj_type in ['raw', 'mm'], 'only `raw` or `mm` is supported'

    time_format = '%Y/%m/%d %H:%M:%S'
    with open(input_path, 'r') as f:
        trajs = []
        pt_list = []
        tid = None
        for line in f.readlines():
            attrs = line.rstrip().split(',')
            if attrs[0] == '#':
                if len(pt_list) != 0:
                    traj = Trajectory(oid, tid, pt_list)
                    trajs.append(traj)
                oid = attrs[2]
                tid = attrs[1]
                pt_list = []
            else:
                lat = float(attrs[1])
                lng = float(attrs[2])
                if traj_type == 'raw':
                    data = None
                    if extra_fields is not None:
                        data = {}
                        field_idx = 3
                        for field in extra_fields:
                            if field == 'stay':
                                if attrs[field_idx] == 'True':
                                    data[field] = True
                                elif attrs[field_idx] == 'False':
                                    data[field] = False
                                else:
                                    raise Exception('unknown stay status')
                            else:
                                data[field] = attrs[field_idx]
                            field_idx += 1
                    pt = STPoint(lat, lng, datetime.strptime(attrs[0], time_format), data)
                elif traj_type == 'mm':
                    if attrs[3] == 'None':
                        candi_pt = None
                    else:
                        eid = int(attrs[3])
                        proj_lat = float(attrs[4])
                        proj_lng = float(attrs[5])
                        error = float(attrs[6])
                        offset = float(attrs[7])
                        candi_pt = CandidatePoint(proj_lat, proj_lng, eid, error, offset)
                    pt = STPoint(lat, lng, datetime.strptime(attrs[0], time_format), {'candi_pt': candi_pt})
                pt_list.append(pt)
        if len(pt_list) != 0:
            traj = Trajectory(oid, tid, pt_list)
            trajs.append(traj)
        return trajs


def store_traj_file(trajs, target_path, traj_type='raw', extra_fields=None):
    assert traj_type in ['raw', 'mm'], 'only `raw` or `mm` is supported'

    time_format = '%Y/%m/%d %H:%M:%S'
    with open(target_path, 'w') as f:
        for traj in trajs:
            pt_list = traj.pt_list
            f.write('#,{},{},{},{},{} km\n'.format(traj.tid, traj.oid, pt_list[0].time.strftime(time_format),
                                                   pt_list[-1].time.strftime(time_format), traj.length() / 1000))
            if traj_type == 'raw':
                for pt in pt_list:
                    f.write('{},{},{}'.format(pt.time.strftime(time_format), pt.lat, pt.lng))
                    if extra_fields is not None:
                        for extra_field in extra_fields:
                            f.write(',{}'.format(pt.data[extra_field]))
                    f.write('\n')
            elif traj_type == 'mm':
                for pt in pt_list:
                    candi_pt = pt.data['candi_pt']
                    if candi_pt is not None:
                        f.write('{},{},{},{},{},{},{},{}\n'.format(pt.time.strftime(time_format), pt.lat, pt.lng,
                                                                   candi_pt.eid, candi_pt.lat, candi_pt.lng,
                                                                   candi_pt.error, candi_pt.offset))
                    else:
                        f.write('{},{},{},None,None,None,None,None\n'.format(
                            pt.time.strftime(time_format), pt.lat, pt.lng))
