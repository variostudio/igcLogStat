import folium


def convert(str_coord):
    deg = str_coord[0:2]
    ll = len(str_coord)
    three_last = str_coord[ll - 3:ll]
    mins = str_coord[2:ll - 3]

    res = int(deg) + int(mins)/60 + int(three_last)/60/1000
    return res


def get_pos(file_item, pts):
    if file_item.startswith('B'):
        lat = file_item[7:14]
        lon = file_item[16:23]

        n_lat = convert(lat)
        n_lon = -convert(lon)

        pts.append([n_lat, n_lon])


if __name__ == '__main__':
    points = []

    with open('files/file1.igc') as f:
        for line in f:
            get_pos(line, points)

    base_map = folium.Map(points[0], zoom_start=14)
    folium.PolyLine(
        points, color='darkorange'
    ).add_to(base_map)
    base_map.save('test.html')
