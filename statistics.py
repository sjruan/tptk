from .common.trajectory import parse_traj_file
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import numpy as np
from matplotlib.ticker import PercentFormatter
import json


def statistics(traj_dir):
    path = [item for item in traj_dir.split('/') if len(item) != 0]
    stat_dirname = path[-1] + '_stat/'
    stat_dir = '/'.join(path[:-1] + [stat_dirname])
    os.makedirs(stat_dir, exist_ok=True)

    length_data = []
    duration_data = []
    seq_len_data = []
    traj_avg_time_interval_data = []
    traj_avg_dist_interval_data = []
    oids = set()
    tot_pts = 0
    tot_trajs = 0
    stats = {}

    for filename in tqdm(os.listdir(traj_dir)):
        trajs = parse_traj_file(os.path.join(traj_dir, filename))
        tot_trajs += len(trajs)
        for traj in trajs:
            oids.add(traj.oid)
            nb_pts = len(traj.pt_list)
            tot_pts += nb_pts
            seq_len_data.append(nb_pts)
            length_data.append(traj.get_length() / 1000.0)
            duration_data.append(traj.get_duration() / 60.0)
            traj_avg_time_interval_data.append(traj.get_time_interval())
            traj_avg_dist_interval_data.append(traj.get_distance_interval())
    print('#objects:{}'.format(len(oids)))
    print('#points:{}'.format(tot_pts))
    print('#trajectories:{}'.format(tot_trajs))
    stats['#objects'] = len(oids)
    stats['#points'] = tot_pts
    stats['#trajectories'] = tot_trajs
    with open(os.path.join(stat_dir, 'stats.json'), 'w') as f:
        json.dump(stats, f)

    plt.hist(seq_len_data, weights=np.ones(len(seq_len_data)) / len(seq_len_data))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel('#Points')
    plt.ylabel('Percentage')
    plt.savefig(os.path.join(stat_dir, 'nb_points_dist.png'))
    plt.clf()

    plt.hist(length_data, weights=np.ones(len(length_data)) / len(length_data))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel('Length (KM)')
    plt.ylabel('Percentage')
    plt.savefig(os.path.join(stat_dir, 'length_dist.png'))
    plt.clf()

    plt.hist(duration_data, weights=np.ones(len(duration_data)) / len(duration_data))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel('Duration (Min)')
    plt.ylabel('Percentage')
    plt.savefig(os.path.join(stat_dir, 'duration_dist.png'))
    plt.clf()

    plt.hist(traj_avg_time_interval_data,
             weights=np.ones(len(traj_avg_time_interval_data)) / len(traj_avg_time_interval_data))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel('Time Interval (Sec)')
    plt.ylabel('Percentage')
    plt.savefig(os.path.join(stat_dir, 'time_interval_dist.png'))
    plt.clf()

    plt.hist(traj_avg_dist_interval_data,
             weights=np.ones(len(traj_avg_dist_interval_data)) / len(traj_avg_dist_interval_data))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel('Distance Interval (Meter)')
    plt.ylabel('Percentage')
    plt.savefig(os.path.join(stat_dir, 'distance_interval_dist.png'))
    plt.clf()
