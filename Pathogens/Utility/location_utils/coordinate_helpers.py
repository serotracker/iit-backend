def is_point_in_bounding_box(point: [float, float], bounding_box: [float, float, float, float]):
    point_longitude = point[0]
    point_latitude = point[1]
    bounding_box_longitude_minimum = bounding_box[0]
    bounding_box_latitude_minimum = bounding_box[1]
    bounding_box_longitude_maximum = bounding_box[2]
    bounding_box_latitude_maximum = bounding_box[3]

    return point_longitude >= bounding_box_longitude_minimum and point_longitude <= bounding_box_longitude_maximum and point_latitude >= bounding_box_latitude_minimum and point_latitude <= bounding_box_latitude_maximum 