import math
DEGREES_TO_RADIANS = math.pi / 180
RADIANS_TO_DEGREES = 1 / DEGREES_TO_RADIANS
EARTH_MEAN_RADIUS_METER = 6371008.7714
DEG_TO_KM = DEGREES_TO_RADIANS * EARTH_MEAN_RADIUS_METER
LAT_PER_METER = 8.993203677616966e-06
LNG_PER_METER = 1.1700193970443768e-05


class SPoint:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return '({},{})'.format(self.lat, self.lng)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng

    def __ne__(self, other):
        return not self == other


# returns the distance in meters between two points specified in degrees (Haversine formula).
def distance(a, b):
    return haversine_distance(a, b)


# http://www.movable-type.co.uk/scripts/latlong.html
def bearing(a, b):
    pt_a_lat_rad = math.radians(a.lat)
    pt_a_lng_rad = math.radians(a.lng)
    pt_b_lat_rad = math.radians(b.lat)
    pt_b_lng_rad = math.radians(b.lng)
    y = math.sin(pt_b_lng_rad - pt_a_lng_rad) * math.cos(pt_b_lat_rad)
    x = math.cos(pt_a_lat_rad) * math.sin(pt_b_lat_rad) - math.sin(pt_a_lat_rad) * math.cos(pt_b_lat_rad) * math.cos(pt_b_lng_rad - pt_a_lng_rad)
    bearing_rad = math.atan2(y, x)
    return math.fmod(math.degrees(bearing_rad) + 360.0, 360.0)


def project_pt_to_segment(a, b, t):
    ab_angle = bearing(a, b)
    at_angle = bearing(a, t)
    ab_length = distance(a, b)
    at_length = distance(a, t)
    delta_angle = at_angle - ab_angle
    meters_along = at_length * math.cos(math.radians(delta_angle))
    if ab_length == 0.0:
        rate = 0.0
    else:
        rate = meters_along / ab_length
    if rate >= 1:
        projection = SPoint(b.lat, b.lng)
        rate = 1.0
    elif rate <= 0:
        projection = SPoint(a.lat, a.lng)
        rate = 0.0
    else:
        projection = cal_loc_along_line(a, b, rate)
    dist = distance(t, projection)
    return projection, rate, dist


# line has no end points, so the projection may be out of the segment
def project_pt_to_line(a, b, t):
    ab_angle = bearing(a, b)
    at_angle = bearing(a, t)
    ab_length = distance(a, b)
    at_length = distance(a, t)
    delta_angle = at_angle - ab_angle
    meters_along = at_length * math.cos(math.radians(delta_angle))
    if ab_length == 0.0:
        rate = 0.0
    else:
        rate = meters_along / ab_length
    projection = cal_loc_along_line(a, b, rate)
    dist = distance(t, projection)
    return projection, rate, dist


def haversine_distance(a, b):
    if same_coords(a, b):
        return 0.0
    delta_lat = math.radians(b.lat - a.lat)
    delta_lng = math.radians(b.lng - a.lng)
    h = math.sin(delta_lat / 2.0) * math.sin(delta_lat / 2.0) + math.cos(math.radians(a.lat)) * math.cos(
        math.radians(b.lat)) * math.sin(delta_lng / 2.0) * math.sin(delta_lng / 2.0)
    c = 2.0 * math.atan2(math.sqrt(h), math.sqrt(1 - h))
    d = EARTH_MEAN_RADIUS_METER * c
    return d


def same_coords(a, b):
    if a.lat == b.lat and a.lng == b.lng:
        return True
    else:
        return False


def cal_loc_along_line(a, b, rate):
    lat = a.lat + rate * (b.lat - a.lat)
    lng = a.lng + rate * (b.lng - a.lng)
    return SPoint(lat, lng)


def angle(a, b, c, d):
    """
    v1 a b
    v2 c d
    calculate angle between AB and CD
    :param v1:
    :param v2:
    :return:
    """
    dx1 = b.lng - a.lng
    dy1 = b.lat - a.lat
    dx2 = d.lng - c.lng
    dy2 = d.lat - c.lat
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180/math.pi)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180/math.pi)
    if angle1*angle2 >= 0:
        included_angle = abs(angle1-angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    return included_angle
