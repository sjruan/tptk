from datetime import datetime


class PathEntity:
    def __init__(self, enter_time, leave_time, eid):
        self.enter_time = enter_time
        self.leave_time = leave_time
        self.eid = eid


class Path:
    def __init__(self, oid, pid, path_entities):
        self.oid = oid
        self.pid = pid
        self.path_entities = path_entities


def parse_path_file(input_path):
    time_format = '%Y-%m-%d %H:%M:%S.%f'
    paths = []
    with open(input_path, 'r') as f:
        path_entities = []
        pid = None
        for line in f.readlines():
            attrs = line.rstrip().split(',')
            if attrs[0] == '#':
                if len(path_entities) != 0:
                    paths.append(Path(oid, pid, path_entities))
                oid = attrs[2]
                pid = attrs[1]
                path_entities = []
            else:
                enter_time = datetime.strptime(attrs[0], time_format)
                leave_time = datetime.strptime(attrs[1], time_format)
                eid = int(attrs[2])
                path_entities.append(PathEntity(enter_time, leave_time, eid))
        if len(path_entities) != 0:
            paths.append(Path(oid, pid, path_entities))
    return paths


def store_path_file(paths, target_path):
    with open(target_path, 'w') as f:
        for path in paths:
            path_entities = path.path_entities
            f.write('#,{},{},{},{}\n'.format(path.pid, path.oid,
                                             path_entities[0].enter_time.isoformat(sep=' ', timespec='milliseconds'),
                                             path_entities[-1].leave_time.isoformat(sep=' ', timespec='milliseconds')))
            for path_entity in path_entities:
                f.write('{},{},{}\n'.format(path_entity.enter_time.isoformat(sep=' ', timespec='milliseconds'),
                                            path_entity.leave_time.isoformat(sep=' ', timespec='milliseconds'),
                                            path_entity.eid))
